function effectsToJson() {
    const effectDivs = document.getElementsByClassName('effect-element');
    let effectsJson = [];

    for (let i = 0; i < effectDivs.length; i++) {
        const card = effectDivs[i];
        let current_effectJson = {};

        // Read the pedal type from the title <h3> inside the header
        const titleEl = card.querySelector('.pedal-title');
        if (titleEl) {
            current_effectJson['type'] = titleEl.textContent;
        }

        // Read all knob values from hidden inputs nested anywhere in the card
        const knobInputs = card.querySelectorAll('input[type="hidden"]');
        knobInputs.forEach((input) => {
            if (input.id) {
                current_effectJson[input.id.toString().toLowerCase()] = input.value;
            }
        });

        effectsJson.push(current_effectJson);
    }

    const result = JSON.stringify(effectsJson);
    console.log(result);
    return result;
}

onFormSubmission = async () => {
    const baseURL = 'http://127.0.0.1:8000/process-image/?effects_json=';
    const url = 'http://localhost:8000/process-image/?effects_json=%5B%7B%22type%22%3A%20%22Delay%22%7D%5D'
    const form = document.getElementById('image-form');
    const formData = new FormData(form);
    effectsToJson();
    const response = await fetch(baseURL + effectsToJson(), {
        method: 'POST',
        body: formData
    })
    const blob = await response.blob();
    if (response.status !== 200) {
        console.log(response.statusText);
        return;
    }
    const imgUrl = URL.createObjectURL(blob);
    document.getElementById('processed-image').src = imgUrl;
};

const form = document.querySelector("#image-form");
form.addEventListener("submit", (event) => {
    event.preventDefault();
    onFormSubmission();
});