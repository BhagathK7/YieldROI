// ============================================================
// YieldROI Frontend
// ============================================================


// ============================================================
// LANGUAGE DATA
// ============================================================

const translations = {

    en: {

        languageButton: "தமிழ்",

        districtPlaceholder: "Select District",
        cropPlaceholder: "Select Crop",
        seasonPlaceholder: "Select Season",
        yearPlaceholder: "Select Year",

        areaPlaceholder: "Enter area",

        predicting: "Analyzing...",
        predict: "Predict & Analyze",

        error:
            "Something went wrong. Please try again.",

        networkError:
            "Unable to connect to the server. Please make sure the Flask application is running."

    },

    ta: {

        languageButton: "English",

        districtPlaceholder:
            "மாவட்டத்தைத் தேர்ந்தெடுக்கவும்",

        cropPlaceholder:
            "பயிரைத் தேர்ந்தெடுக்கவும்",

        seasonPlaceholder:
            "பருவத்தைத் தேர்ந்தெடுக்கவும்",

        yearPlaceholder:
            "ஆண்டைத் தேர்ந்தெடுக்கவும்",

        areaPlaceholder:
            "பரப்பளவை உள்ளிடவும்",

        predicting:
            "பகுப்பாய்வு செய்யப்படுகிறது...",

        predict:
            "கணித்து பகுப்பாய்வு செய்க",

        error:
            "ஏதோ தவறு ஏற்பட்டுள்ளது. மீண்டும் முயற்சிக்கவும்.",

        networkError:
            "சேவையகத்துடன் இணைக்க முடியவில்லை. Flask பயன்பாடு இயங்குகிறதா என்பதை உறுதிப்படுத்தவும்."

    }

};


// ============================================================
// TAMIL TRANSLATIONS FOR DROPDOWN VALUES
// ============================================================

const districtTamil = {

    "Ariyalur": "அரியலூர்",
    "Chengalpattu": "செங்கல்பட்டு",
    "Chennai": "சென்னை",
    "Coimbatore": "கோயம்புத்தூர்",
    "Cuddalore": "கடலூர்",
    "Dharmapuri": "தர்மபுரி",
    "Dindigul": "திண்டுக்கல்",
    "Erode": "ஈரோடு",
    "Kallakurichi": "கள்ளக்குறிச்சி",
    "Kancheepuram": "காஞ்சிபுரம்",
    "Karur": "கரூர்",
    "Krishnagiri": "கிருஷ்ணகிரி",
    "Madurai": "மதுரை",
    "Mayiladuthurai": "மயிலாடுதுறை",
    "Nagapattinam": "நாகப்பட்டினம்",
    "Namakkal": "நாமக்கல்",
    "Perambalur": "பெரம்பலூர்",
    "Pudukkottai": "புதுக்கோட்டை",
    "Ramanathapuram": "ராமநாதபுரம்",
    "Ranipet": "ராணிப்பேட்டை",
    "Salem": "சேலம்",
    "Sivaganga": "சிவகங்கை",
    "Tenkasi": "தென்காசி",
    "Thanjavur": "தஞ்சாவூர்",
    "Theni": "தேனி",
    "Thoothukudi": "தூத்துக்குடி",
    "Tiruchirappalli": "திருச்சிராப்பள்ளி",
    "Tirunelveli": "திருநெல்வேலி",
    "Tirupathur": "திருப்பத்தூர்",
    "Tiruppur": "திருப்பூர்",
    "Tiruvallur": "திருவள்ளூர்",
    "Tiruvannamalai": "திருவண்ணாமலை",
    "Tiruvarur": "திருவாரூர்",
    "Vellore": "வேலூர்",
    "Viluppuram": "விழுப்புரம்",
    "Virudhunagar": "விருதுநகர்",

    "The Nilgiris": "நீலகிரி"
};


const cropTamil = {

    "Rice": "நெல்",
    "Paddy": "நெல்",

    "Maize": "மக்காச்சோளம்",

    "Ragi": "கேழ்வரகு",

    "Groundnut": "நிலக்கடலை",

    "Sugarcane": "கரும்பு",

    "Cotton": "பருத்தி",

    "Sesamum": "எள்",

    "Gingelly": "எள்",

    "Black Gram": "உளுந்து",
    "Blackgram": "உளுந்து",

    "Green Gram": "பாசிப்பயறு",
    "Greengram": "பாசிப்பயறு",

    "Horse Gram": "கொள்ளு",
    "Horsegram": "கொள்ளு",

    "Cowpea": "தட்டைப்பயறு",

    "Sorghum": "சோளம்",
    "Jowar": "சோளம்",

    "Bajra": "கம்பு",

    "Cumbu": "கம்பு",

    "Chillies": "மிளகாய்",

    "Onion": "வெங்காயம்",

    "Potato": "உருளைக்கிழங்கு",

    "Tapioca": "மரவள்ளிக்கிழங்கு",

    "Turmeric": "மஞ்சள்",

    "Banana": "வாழை",

    "Coconut": "தேங்காய்",

    "Garlic": "பூண்டு",

    "Ginger": "இஞ்சி",

    "Tomato": "தக்காளி",

    "Brinjal": "கத்தரிக்காய்",

    "Lady's Finger": "வெண்டைக்காய்",

    "Cashew Nut": "முந்திரி",

    "Cashewnut": "முந்திரி",

    "Tobacco": "புகையிலை",

    "Sunflower": "சூரியகாந்தி",

    "Rapeseed and Mustard": "கடுகு",

    "Coriander": "கொத்தமல்லி",

    "Arecanut": "பாக்கு",

    "Cardamom": "ஏலக்காய்",

    "Pepper": "மிளகு",

    "Black Pepper": "மிளகு"
};


const seasonTamil = {

    "Kharif": "காரிப் பருவம்",

    "Rabi": "ரபிப் பருவம்",

    "Whole Year": "ஆண்டு முழுவதும்",

    "Summer": "கோடைப் பருவம்",

    "Winter": "குளிர்காலம்",

    "Autumn": "இலையுதிர் பருவம்",

    "Kharif & Rabi": "காரிப் & ரபிப் பருவம்"
};


// ============================================================
// CURRENT LANGUAGE
// ============================================================

let currentLanguage = "en";


// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        setupYears();

        setupDropdownTranslations();

        setupForm();

        applyLanguage();

    }
);


// ============================================================
// YEAR SETUP
// ============================================================

function setupYears() {

    const yearSelect =
        document.getElementById("year");

    if (!yearSelect) {
        return;
    }


    // Model training data covers 1997-2022.
    // We keep the prediction interface within
    // the historical model range.

    for (
        let year = 2022;
        year >= 1997;
        year--
    ) {

        const option =
            document.createElement("option");

        option.value = year;

        option.textContent = year;

        yearSelect.appendChild(option);
    }
}


// ============================================================
// DROPDOWN TRANSLATIONS
// ============================================================

function setupDropdownTranslations() {

    translateSelect(
        "district",
        districtTamil
    );

    translateSelect(
        "crop",
        cropTamil
    );

    translateSelect(
        "season",
        seasonTamil
    );

    translateYearSelect();

}


// ------------------------------------------------------------
// Translate normal select
// ------------------------------------------------------------

function translateSelect(
    selectId,
    tamilDictionary
) {

    const select =
        document.getElementById(selectId);

    if (!select) {
        return;
    }


    const options =
        select.querySelectorAll("option");


    options.forEach(
        function (option) {

            const value =
                option.value;


            if (!value) {
                return;
            }


            option.dataset.english =
                value;


            option.dataset.tamil =
                tamilDictionary[value] ||
                value;

        }
    );
}


// ------------------------------------------------------------
// Translate years
// ------------------------------------------------------------

function translateYearSelect() {

    const select =
        document.getElementById("year");

    if (!select) {
        return;
    }


    const options =
        select.querySelectorAll("option");


    options.forEach(
        function (option) {

            if (!option.value) {
                return;
            }

            option.dataset.english =
                option.value;

            option.dataset.tamil =
                option.value;
        }
    );
}


// ============================================================
// LANGUAGE SWITCH
// ============================================================

function toggleLanguage() {

    currentLanguage =
        currentLanguage === "en"
            ? "ta"
            : "en";


    applyLanguage();

}


// ============================================================
// APPLY LANGUAGE
// ============================================================

function applyLanguage() {

    document.documentElement.lang =
        currentLanguage === "ta"
            ? "ta"
            : "en";


    document.body.classList.toggle(
        "tamil-mode",
        currentLanguage === "ta"
    );


    // --------------------------------------------------------
    // Show/hide bilingual elements
    // --------------------------------------------------------

    const englishElements =
        document.querySelectorAll(
            ".language-en"
        );


    const tamilElements =
        document.querySelectorAll(
            ".language-ta"
        );


    englishElements.forEach(
        function (element) {

            element.style.display =
                currentLanguage === "en"
                    ? ""
                    : "none";

        }
    );


    tamilElements.forEach(
        function (element) {

            element.style.display =
                currentLanguage === "ta"
                    ? ""
                    : "none";

        }
    );


    // --------------------------------------------------------
    // Language button
    // --------------------------------------------------------

    const languageButton =
        document.getElementById(
            "languageSwitch"
        );


    if (languageButton) {

        languageButton.textContent =
            translations[
                currentLanguage
            ].languageButton;

    }


    // --------------------------------------------------------
    // Placeholders
    // --------------------------------------------------------

    const area =
        document.getElementById("area");


    if (area) {

        area.placeholder =
            translations[
                currentLanguage
            ].areaPlaceholder;

    }


    // --------------------------------------------------------
    // Select placeholders
    // --------------------------------------------------------

    updateSelectPlaceholder(
        "district",
        translations[
            currentLanguage
        ].districtPlaceholder
    );


    updateSelectPlaceholder(
        "crop",
        translations[
            currentLanguage
        ].cropPlaceholder
    );


    updateSelectPlaceholder(
        "season",
        translations[
            currentLanguage
        ].seasonPlaceholder
    );


    updateSelectPlaceholder(
        "year",
        translations[
            currentLanguage
        ].yearPlaceholder
    );


    // --------------------------------------------------------
    // Dropdown values
    // --------------------------------------------------------

    updateSelectOptions(
        "district"
    );

    updateSelectOptions(
        "crop"
    );

    updateSelectOptions(
        "season"
    );

    updateSelectOptions(
        "year"
    );

}


// ============================================================
// SELECT PLACEHOLDER
// ============================================================

function updateSelectPlaceholder(
    selectId,
    placeholder
) {

    const select =
        document.getElementById(selectId);

    if (!select) {
        return;
    }


    const firstOption =
        select.querySelector(
            "option[value='']"
        );


    if (firstOption) {

        firstOption.textContent =
            placeholder;

    }
}


// ============================================================
// SELECT OPTION LANGUAGE
// ============================================================

function updateSelectOptions(
    selectId
) {

    const select =
        document.getElementById(selectId);

    if (!select) {
        return;
    }


    const options =
        select.querySelectorAll(
            "option"
        );


    options.forEach(
        function (option) {

            if (!option.value) {
                return;
            }


            if (
                currentLanguage === "ta"
            ) {

                option.textContent =
                    option.dataset.tamil ||
                    option.value;

            } else {

                option.textContent =
                    option.dataset.english ||
                    option.value;

            }

        }
    );

}


// ============================================================
// SCROLL TO FORM
// ============================================================

function scrollToPrediction() {

    const section =
        document.getElementById(
            "predictionSection"
        );


    if (!section) {
        return;
    }


    section.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


// ============================================================
// FORM
// ============================================================

function setupForm() {

    const form =
        document.getElementById(
            "predictionForm"
        );


    if (!form) {
        return;
    }


    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            await submitPrediction(form);

        }
    );

}


// ============================================================
// SUBMIT PREDICTION
// ============================================================

async function submitPrediction(
    form
) {

    const button =
        document.getElementById(
            "predictButton"
        );


    const errorBox =
        document.getElementById(
            "formError"
        );


    errorBox.textContent = "";


    // --------------------------------------------------------
    // Get values
    // --------------------------------------------------------

    const district =
        document.getElementById(
            "district"
        ).value;


    const crop =
        document.getElementById(
            "crop"
        ).value;


    const season =
        document.getElementById(
            "season"
        ).value;


    const year =
        document.getElementById(
            "year"
        ).value;


    const area =
        document.getElementById(
            "area"
        ).value;


    // --------------------------------------------------------
    // Validation
    // --------------------------------------------------------

    if (
        !district ||
        !crop ||
        !season ||
        !year ||
        !area
    ) {

        errorBox.textContent =
            translations[
                currentLanguage
            ].error;

        return;
    }


    if (
        Number(area) <= 0
    ) {

        errorBox.textContent =
            currentLanguage === "ta"
                ? "பரப்பளவு 0-ஐ விட அதிகமாக இருக்க வேண்டும்."
                : "Area must be greater than zero.";

        return;
    }


    // --------------------------------------------------------
    // Loading state
    // --------------------------------------------------------

    button.classList.add(
        "loading"
    );

    button.disabled = true;


    // --------------------------------------------------------
    // Data
    // --------------------------------------------------------

    const payload = {

        district: district,

        crop: crop,

        season: season,

        year: Number(year),

        area: Number(area)

    };


    try {

        const response =
            await fetch(
                "/predict",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(payload)
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.error ||
                translations[
                    currentLanguage
                ].error
            );

        }


        if (!result.success) {

            throw new Error(
                result.error ||
                translations[
                    currentLanguage
                ].error
            );

        }


        // ----------------------------------------------------
        // Store language for result page
        // ----------------------------------------------------

        sessionStorage.setItem(
            "yieldroi_language",
            currentLanguage
        );


        // ----------------------------------------------------
        // Open result page
        // ----------------------------------------------------

        const encoded =
            encodeURIComponent(
                JSON.stringify(result)
            );


        window.location.href =
            "/result?data=" + encoded;


    } catch (error) {

        console.error(
            "Prediction error:",
            error
        );


        errorBox.textContent =
            error.message ||
            translations[
                currentLanguage
            ].networkError;


    } finally {

        button.classList.remove(
            "loading"
        );

        button.disabled = false;

    }

}