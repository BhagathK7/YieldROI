document.addEventListener("DOMContentLoaded", () => {

    /* ===============================================
       NAVIGATION
    =============================================== */

    const navLinks = document.querySelectorAll("nav a");

    navLinks.forEach(link => {

        link.addEventListener("click", () => {

            navLinks.forEach(item => {
                item.classList.remove("active");
            });

            link.classList.add("active");

        });

    });


    /* ===============================================
       PREDICTION FORM
    =============================================== */

    const predictionForm =
        document.querySelector(".predict-card");


    if (predictionForm) {

        predictionForm.addEventListener(
            "submit",
            () => {

                const button =
                    predictionForm.querySelector(
                        ".predict-button"
                    );


                if (!button) {
                    return;
                }


                button.classList.add("loading");

                button.disabled = true;

                button.setAttribute(
                    "aria-busy",
                    "true"
                );

                button.innerHTML = `
                    <span class="loading-symbol">
                        ◌
                    </span>
                    Analyzing...
                `;

            }
        );

    }


    /* ===============================================
       RESULT PAGE ANIMATION
    =============================================== */

    const resultPage =
        document.querySelector(".result-page");


    if (resultPage) {

        requestAnimationFrame(() => {

            resultPage.classList.add(
                "result-loaded"
            );

        });

    }


    /* ===============================================
       NUMBER ANIMATION
    =============================================== */

    const metricNumbers =
        document.querySelectorAll(
            ".big-yield, .metric-large"
        );


    metricNumbers.forEach(element => {

        element.style.opacity = "0";

        element.style.transform =
            "translateY(10px)";


        setTimeout(() => {

            element.style.transition =
                "opacity .5s ease, transform .5s ease";

            element.style.opacity = "1";

            element.style.transform =
                "translateY(0)";

        }, 120);

    });


    /* ===============================================
       SMOOTH INTERNAL NAVIGATION
    =============================================== */

    const internalLinks =
        document.querySelectorAll(
            'nav a[href^="#"]'
        );


    internalLinks.forEach(link => {

        link.addEventListener(
            "click",
            event => {

                const targetId =
                    link.getAttribute("href");

                const target =
                    document.querySelector(targetId);


                if (!target) {
                    return;
                }


                event.preventDefault();


                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }
        );

    });

});