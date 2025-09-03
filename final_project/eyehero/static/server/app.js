// ==========================
//      Import Modules
// ==========================
const express = require("express"); // Express framework for server
const cors = require("cors"); // Enable Cross-Origin requests
const webpush = require("web-push"); // Library for push notifications
const bodyParser = require("body-parser"); // Parse incoming JSON requests
const sqlite3 = require("sqlite3").verbose(); // SQLite database

// ==========================
//      Initialize App
// ==========================
const app = express();
app.use(cors()); // Allow CORS for all routes
app.use(bodyParser.json()); // Parse JSON request bodies

// ==========================
//      VAPID Keys for Web Push
// ==========================
// These keys are required for sending push notifications via the Push API
const publicKey = "BINcxKfrJeXNEBUWpsNNtqSv_U-mXZSQbfG2gpa93U_x5cX7oneS3EyUXc4GirxZXjXRBKYbeZslu930EsJHBKS";
const privateKey = "QaaHBEnLOH07tgdSwJ2W3tOfRkjZ25uRUs8vLqeSD4g";

// Configure web-push with VAPID keys
webpush.setVapidDetails(
    "mailto:mnnnwzk.7@gmail.com", // Contact email
    publicKey,
    privateKey
);

// ==========================
//      Database Setup
// ==========================
const path = require("path");
const dbPath = path.resolve(__dirname, "../../db/eyehero.db");

// Connect to SQLite database
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error("❌ Error opening database:", err.message);
    } else {
        console.log("✅ Connected to SQLite:", dbPath);
    }
});

// ==========================
//      Routes
// ==========================

// POST /sendNotification
// Sends a push notification to all subscriptions stored in the database
app.post("/sendNotification", (req, res) => {
    const {
        title,
        body
    } = req.body; // Notification title and body
    const payload = JSON.stringify({
        title,
        body
    });

    // Retrieve all subscriptions from DB
    db.all("SELECT subscription FROM push_subscriptions", [], async (err, rows) => {
        if (err) return res.status(500).json({
            success: false,
            error: err.message
        });

        // Send notification to each subscription
        const sendPromises = rows.map(row =>
            webpush.sendNotification(JSON.parse(row.subscription), payload)
        );

        try {
            await Promise.all(sendPromises);
            res.json({
                success: true
            }); // All notifications sent successfully
        } catch (err) {
            console.error("❌ Error sending notifications:", err);
            res.status(500).json({
                success: false,
                error: err
            });
        }
    });
});

// POST /subscribe
// Receives a new subscription from the frontend and stores it in the database
app.post("/subscribe", (req, res) => {
    const sub = JSON.stringify(req.body);

    db.run("INSERT INTO push_subscriptions (subscription) VALUES (?)", [sub], function(err) {
        if (err) return res.status(500).json({
            success: false,
            error: err.message
        });
        res.status(201).json({
            success: true
        }); // Subscription added successfully
    });
});

// ==========================
//      Start Server
// ==========================
const PORT = 4000;
app.listen(PORT, () => console.log(`✅ Push server running on port ${PORT}`));
