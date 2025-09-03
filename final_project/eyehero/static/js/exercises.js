/**
 * Exercise Routine Script
 * Handles the step-by-step execution of morning/night eye exercises.
 * Features: timer, audio beep, avatar updates, and progress reporting.
 */

document.addEventListener("DOMContentLoaded", () => {

    // ----------------- DOM Elements -----------------
    const buttonsDiv = document.querySelector(".rule-buttons"); // Container for start/next/finish buttons

    // Insert initial instruction text
    buttonsDiv.innerHTML = `
        <p class="text-start">
            <strong>Tip:</strong> Keep your head still and move only your eyes.<br>
            <strong>Press Start when ready!</strong>
        </p>
    `;

    // Create start button
    const timerBtn = document.createElement("button");
    timerBtn.textContent = "Start";
    timerBtn.classList.add("btn-yellow", "mb-3");
    buttonsDiv.appendChild(timerBtn);

    const beep = new Audio('/static/sound/beep.mp3'); // Beep sound for exercise transitions

    // Determine exercise mode (morning/night)
    const mode = document.body.dataset.mode || "morning";

    // ----------------- Exercise Configurations -----------------
    const configs = {
        morning: [{
                name: "Eye Rolling",
                subExercises: [{
                        instruction: "Move your eyes <strong>up</strong> and <strong>down</strong> smoothly.",
                        duration: 10
                    },
                    {
                        instruction: "Move your eyes <strong>left</strong> and <strong>right</strong> smoothly.",
                        duration: 10
                    },
                    {
                        instruction: "Rotate your eyes in a <strong>circle</strong> clockwise and counterclockwise, each <strong>10s</strong>.",
                        duration: 20
                    },
                    {
                        instruction: "Move your eyes in <strong>figure-8</strong> pattern clockwise and counterclockwise, each <strong>10s</strong>.",
                        duration: 20
                    }
                ]
            },
            {
                name: "Near-Far Focus",
                subExercises: [{
                        instruction: "Hold your thumb about <strong>10 inches</strong> from your face and focus on it.",
                        duration: 10
                    },
                    {
                        instruction: "Now shift your gaze to a distant object at least <strong>20 feet</strong> away and focus on that.",
                        duration: 10
                    }
                ]
            },
            {
                name: "Blinking",
                subExercises: [{
                    instruction: "Gently <strong>close</strong> and <strong>open</strong> your eyes, focusing on full blinks to refresh your eyes.",
                    duration: 15
                }]
            },
            {
                name: "Palming",
                subExercises: [{
                    instruction: "Gently <strong>cover</strong> your eyes with your hands and take a deep, calming breath.",
                    duration: 15
                }]
            },
            {
                name: "Neck/Shoulder Stretch",
                subExercises: [{
                    instruction: "Gently <strong>stretch</strong> your neck and shoulders, move slowly, breathe deeply, and relax to ease eye strain.",
                    duration: 15
                }]
            }
        ],
        night: [{
                name: "Palming",
                subExercises: [{
                    instruction: "Gently <strong>cover</strong> your eyes with your hands and take a deep, calming breath.",
                    duration: 15
                }]
            },
            {
                name: "Eye Massage",
                subExercises: [{
                    instruction: "With soft <strong>circular motions</strong>, massage the sides and under your eyes to release the day’s tension.",
                    duration: 15
                }]
            },
            {
                name: "Slow Blinking",
                subExercises: [{
                    instruction: "Blink <strong>slowly and gently</strong>, letting each blink relax and soothe your tired eyes.",
                    duration: 15
                }]
            },
            {
                name: "Figure Eight",
                subExercises: [{
                    instruction: "Move your eyes in a slow <strong>figure-8 pattern</strong>, calming and loosening the eye muscles before rest.",
                    duration: 10
                }]
            }
        ]
    };

    const exercises = configs[mode]; // Pick the exercises based on mode

    let currentMainIndex = 0; // Tracks main exercise index
    let currentSubIndex = 0; // Tracks sub-exercise index

    const exerciseNameElem = document.querySelector(".exercise-name");
    const textElem = document.querySelector(".text-start");

    /**
     * Show the "Next" or "Finish" button after current main exercise is completed
     */
    function showNextButton() {
        timerBtn.style.display = "none";

        const isLastMain = currentMainIndex >= exercises.length - 1;

        if (isLastMain) {
            // Display completion message
            exerciseNameElem.innerText = "Exercise Complete ✔";
            textElem.innerHTML = '<p class="text-done">Well Done<strong>!</strong></p>';

            // Update avatar to happy
            const avatar = document.getElementById("avatar");
            if (avatar) {
                const newImg = new Image();
                newImg.src = "/static/images/happy.png";
                newImg.onload = () => {
                    avatar.style.transition = "opacity 0.3s ease";
                    avatar.style.opacity = "0";
                    setTimeout(() => {
                        avatar.src = newImg.src;
                        avatar.style.width = window.innerWidth <= 768 ? "140px" : "280px";
                        avatar.style.height = window.innerWidth <= 768 ? "170px" : "300px";
                        avatar.style.marginBottom = window.innerWidth <= 768 ? "10px" : "5px";
                        avatar.style.opacity = "1";
                    }, 50);
                };
            }

            // Create finish button to post progress
            const finishBtn = document.createElement("button");
            finishBtn.textContent = "FINISH";
            finishBtn.classList.add("btn-yellow", "mb-2");
            buttonsDiv.appendChild(finishBtn);

            finishBtn.addEventListener("click", () => {
                fetch("/progress", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            type: mode
                        })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            window.location.href = "/progress"; // Redirect to progress page
                        }
                    });
            });

        } else {
            // Create "Next" button
            const nextBtn = document.createElement("button");
            nextBtn.textContent = "Next";
            nextBtn.classList.add("btn-yellow", "mb-3");
            buttonsDiv.appendChild(nextBtn);

            nextBtn.addEventListener("click", () => {
                nextBtn.remove();
                timerBtn.style.display = "inline-block";
                timerBtn.disabled = false;

                currentSubIndex = 0; // Reset sub-exercise index
                currentMainIndex++; // Move to next main exercise
                runExercise(); // Start next exercise
            });
        }
    }

    /**
     * Execute current sub-exercise with countdown and transition
     */
    function runExercise() {
        const mainEx = exercises[currentMainIndex];
        const subEx = mainEx.subExercises[currentSubIndex];

        exerciseNameElem.innerText = mainEx.name;
        textElem.innerHTML = subEx.instruction;

        let timeLeft = subEx.duration;
        timerBtn.textContent = `${timeLeft}s`;

        const interval = setInterval(() => {
            timeLeft--;
            timerBtn.textContent = `${timeLeft}s`;

            if (timeLeft <= 0) {
                clearInterval(interval);
                beep.currentTime = 0;
                beep.play().catch(e => console.log("Audio play error:", e));

                currentSubIndex++;

                if (currentSubIndex >= mainEx.subExercises.length) {
                    showNextButton();
                } else {
                    setTimeout(runExercise, 3000); // 3s pause before next sub-exercise
                }
            }
        }, 2000); // interval tick (adjust as needed)
    }

    // Prevent multiple clicks
    let isRunning = false;

    timerBtn.addEventListener("click", () => {
        if (isRunning) return;
        isRunning = true;
        timerBtn.disabled = true;
        runExercise();
    });

});
