/**
 * Push Notifications & Timer Script
 * Handles service worker registration, push subscription, screen timers,
 * avatar updates, and desktop notifications for the EyeHero app.
 */

// ----------------- Push Notification Utilities -----------------

/**
/**
 * Convert a Base64 VAPID key to a Uint8Array required for push subscriptions.
 */
function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, "+").replace(/_/g, "/");
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; i++) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

/**
 * Register the Service Worker for push notifications.
 */
async function registerServiceWorker() {
    if ("serviceWorker" in navigator) {
        const registration = await navigator.serviceWorker.register("/sw.js"); // Register SW script
        console.log("SW registered:", registration);
        return registration;
    }
    return null;
}

/**
 * Subscribe the user to push notifications if not already subscribed.
 */
async function subscribeUser() {
    const registration = await registerServiceWorker();
    if (!registration) return;

    let subscription = await registration.pushManager.getSubscription();
    if (!subscription) {
        try {
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(
                    "BINcxKfrJeXNEBUWpsNNtqSv_U-mXZSQbfG2gpa93U_x5cX7oneS3EyUXc4GirxZXjXRBKYbeZslu930EsJHBKS"
                ),
            });

            await fetch("/subscribe", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(subscription),
            });

            console.log("User subscribed for push notifications");
        } catch (err) {
            console.error("Push subscription failed:", err);
        }
    } else {
        console.log("Already subscribed");
    }
}

/**
 * Auto-subscribe old logged-in users after page load if notifications are allowed.
 */
window.addEventListener("load", async () => {
    if ("Notification" in window && Notification.permission !== "granted") {
        const permission = await Notification.requestPermission();
        if (permission === "granted") {
            await subscribeUser();
        }
    } else if (Notification.permission === "granted") {
        await subscribeUser();
    }
});

// ----------------- Timer & Avatar Elements -----------------
const startButton = document.getElementById("StartButton");
const stopButton = document.getElementById("StopButton");
const avatarImg = document.getElementById("avatar");

// Timer variables
let timerInterval;
let breakInterval;
let timeLeft = 20 * 60;
let onBreak = false;

/**
 * Update avatar image with fade-in effect.
 */
function setAvatar(newSrc) {
    avatarImg.style.opacity = "0";
    const newImg = new Image();
    newImg.src = newSrc;
    newImg.onload = () => {
        avatarImg.src = newSrc;
        avatarImg.style.width = window.innerWidth <= 768 ? "220px" : "250px";
        avatarImg.style.height = window.innerWidth <= 768 ? "240px" : "300px";
        avatarImg.style.opacity = "1";
    };
}

/**
 * Show a desktop notification if permission granted.
 */
function showNotification(title, body) {
    if (Notification.permission !== "granted") return;
    new Notification(title, {
        body
    });
}

// ----------------- Timer Functions -----------------
/**
 * Start the main screen timer.
 */
function startTimer() {
    if (onBreak) return;
    clearInterval(timerInterval);
    timeLeft = 20 * 60; // Timer

    timerInterval = setInterval(() => {
        if (timeLeft < 0) {
            clearInterval(timerInterval);
            startBreak();
            return;
        }
        let minutes = Math.floor(timeLeft / 60);
        let seconds = timeLeft % 60;
        startButton.textContent = `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
        timeLeft--;
    }, 1000);
}

/**
 * Start the 20-second break timer.
 */
function startBreak() {
    onBreak = true;
    let breakTime = 20;
    startButton.disabled = true;
    setAvatar("/static/images/tired.png");

    breakInterval = setInterval(() => {
        if (breakTime < 0) {
            clearInterval(breakInterval);
            endBreak();
            return;
        }
        startButton.textContent = `Break: ${breakTime}s`;
        breakTime--;
    }, 1000);

    // Notify via service worker or fallback to Notification API
    if ("serviceWorker" in navigator && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({
            title: "Break Time ⏳",
            body: "Look 20 feet away 👀",
        });
    } else {
        showNotification("Break Time ⏳", "Look 20 feet away 👀");
    }
}

/**
 * End break and resume work timer.
 */
function endBreak() {
    onBreak = false;
    setAvatar("/static/images/eyehero.png");
    startButton.disabled = false;

    if ("serviceWorker" in navigator && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({
            title: "Back to Work! 🚀",
            body: "Continue your task with energy 💪",
        });
    } else {
        showNotification("Back to Work! 🚀", "Continue your task with energy 💪");
    }

    setTimeout(() => {
        startTimer();
    }, 2000);
}

/**
 * Stop all timers and reset UI.
 */
function stopTimer() {
    clearInterval(timerInterval);
    clearInterval(breakInterval);
    onBreak = false;
    startButton.disabled = false;
    startButton.textContent = "Start";
    setAvatar("/static/images/eyehero.png");
}

// ----------------- Button Event Listeners -----------------
startButton.addEventListener("click", async () => {
    if (Notification.permission !== "granted") {
        const permission = await Notification.requestPermission();
        if (permission !== "granted") return alert("Please enable notifications!");
    }
    await subscribeUser();
    startTimer();
});

stopButton.addEventListener("click", stopTimer); // Stop timer and reset UI
