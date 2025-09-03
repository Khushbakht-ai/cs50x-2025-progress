/**
 * Service Worker for EyeHero App
 * Handles:
 *  - Installation and activation
 *  - Push notifications from server
 *  - Messages from client JS (page)
 */

// ----------------- Install -----------------
self.addEventListener("install", (event) => {
    console.log("Service Worker installed");
    // Activate the SW immediately without waiting
    self.skipWaiting();
});

// ----------------- Activate -----------------
self.addEventListener("activate", (event) => {
    console.log("Service Worker activated");
});

// ----------------- Push Notifications -----------------
self.addEventListener("push", (event) => {
    // Default notification data
    let data = {
        title: "Break Time ⏳",
        body: "Look 20 feet away 👀"
    };

    // Use payload from server if available
    if (event.data) data = event.data.json();

    // Select icon based on notification type
    let icon = "/static/images/eyehero.png";
    if (data.title.includes("Break")) {
        icon = "/static/images/tired.png";
    } else if (data.title.includes("Back to Work")) {
        icon = "/static/images/happy.png";
    }

    // Show notification
    event.waitUntil(
        self.registration.showNotification(data.title, {
            body: data.body,
            icon: icon,
        })
    );
});

// ----------------- Messages from Page JS -----------------
self.addEventListener("message", (event) => {
    const {
        title,
        body
    } = event.data;

    let icon = "/static/images/eyehero.png";
    if (title.includes("Break")) {
        icon = "/static/images/tired.png";
    } else if (title.includes("Back to Work")) {
        icon = "/static/images/happy.png";
    }

    self.registration.showNotification(title, {
        body,
        icon: icon,
    });
});
