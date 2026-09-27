document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // DASHBOARD CHART
    // ==========================================

    const chartCanvas = document.getElementById("statsChart");

    if (chartCanvas && typeof Chart !== "undefined") {

        fetch("/api/stats")
            .then(response => {
                if (!response.ok) {
                    throw new Error("Failed to load statistics");
                }

                return response.json();
            })

            .then(data => {

                new Chart(chartCanvas, {

                    type: "doughnut",

                    data: {
                        labels: [
                            "Patients",
                            "Appointments",
                            "Ambulance",
                            "Blood Requests"
                        ],

                        datasets: [{
                            data: [
                                data.patients,
                                data.appointments,
                                data.ambulance,
                                data.blood
                            ],

                            borderWidth: 0
                        }]
                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: true,

                        plugins: {

                            legend: {
                                position: "bottom",

                                labels: {
                                    padding: 18,
                                    usePointStyle: true
                                }
                            }

                        }

                    }

                });

            })

            .catch(error => {

                console.error(
                    "Dashboard statistics error:",
                    error
                );

            });
    }


    // ==========================================
    // AUTO HIDE FLASH MESSAGES
    // ==========================================

    const flashMessages =
        document.querySelectorAll(".flash");

    if (flashMessages.length > 0) {

        setTimeout(function () {

            flashMessages.forEach(function (message) {

                message.style.transition =
                    "opacity 0.5s ease";

                message.style.opacity = "0";

                setTimeout(function () {

                    message.remove();

                }, 500);

            });

        }, 3500);
    }


    // ==========================================
    // CONFIRM DELETE
    // ==========================================

    const deleteForms =
        document.querySelectorAll(
            "form[data-confirm]"
        );

    deleteForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const message =
                form.getAttribute("data-confirm");

            if (!confirm(message)) {

                event.preventDefault();

            }

        });

    });


    // ==========================================
    // MOBILE NAVIGATION
    // ==========================================

    const nav =
        document.querySelector(".nav");

    const topbar =
        document.querySelector(".topbar");

    if (nav && topbar) {

        // Create mobile menu button
        const menuButton =
            document.createElement("button");

        menuButton.innerHTML = "☰";

        menuButton.className =
            "mobile-menu-btn";

        menuButton.setAttribute(
            "aria-label",
            "Open navigation menu"
        );

        topbar.insertBefore(
            menuButton,
            nav
        );

        menuButton.addEventListener(
            "click",
            function () {

                nav.classList.toggle(
                    "mobile-open"
                );

            }
        );

    }


    // ==========================================
    // FORM SUBMIT BUTTON PROTECTION
    // ==========================================

    const forms =
        document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener(
            "submit",
            function () {

                const submitButton =
                    form.querySelector(
                        'button[type="submit"]'
                    );

                if (submitButton) {

                    // Prevent accidental double click
                    submitButton.disabled = true;

                    const originalText =
                        submitButton.innerText;

                    submitButton.innerText =
                        "Processing...";

                    // Restore after 5 seconds
                    setTimeout(function () {

                        submitButton.disabled =
                            false;

                        submitButton.innerText =
                            originalText;

                    }, 5000);

                }

            }
        );

    });


    // ==========================================
    // PHONE NUMBER VALIDATION
    // ==========================================

    const phoneInputs =
        document.querySelectorAll(
            'input[type="tel"]'
        );

    phoneInputs.forEach(function (input) {

        input.addEventListener(
            "input",
            function () {

                // Keep only numbers, +, spaces and -
                this.value =
                    this.value.replace(
                        /[^0-9+\-\s]/g,
                        ""
                    );

            }
        );

    });


    // ==========================================
    // AGE VALIDATION
    // ==========================================

    const ageInputs =
        document.querySelectorAll(
            'input[name="age"]'
        );

    ageInputs.forEach(function (input) {

        input.addEventListener(
            "input",
            function () {

                let age =
                    parseInt(this.value);

                if (age < 0) {
                    this.value = 0;
                }

                if (age > 120) {
                    this.value = 120;
                }

            }
        );

    });


    // ==========================================
    // BLOOD UNITS VALIDATION
    // ==========================================

    const unitsInputs =
        document.querySelectorAll(
            'input[name="units"]'
        );

    unitsInputs.forEach(function (input) {

        input.addEventListener(
            "input",
            function () {

                let units =
                    parseInt(this.value);

                if (units < 1) {
                    this.value = 1;
                }

            }
        );

    });


    // ==========================================
    // SET MINIMUM APPOINTMENT DATE
    // ==========================================

    const dateInputs =
        document.querySelectorAll(
            'input[name="appointment_date"]'
        );

    const today =
        new Date().toISOString().split("T")[0];

    dateInputs.forEach(function (input) {

        if (!input.getAttribute("min")) {

            input.setAttribute(
                "min",
                today
            );

        }

    });


    // ==========================================
    // CONSOLE MESSAGE
    // ==========================================

    console.log(
        "CareConnect application loaded successfully."
    );

});
