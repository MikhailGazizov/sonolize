function effectsToJson() {
    const effectDivs = document.getElementsByClassName('effect-element');
    let effectsJson = []
    for (effectDiv in effectDivs) {
        let current_effectJson = {}

        for(knob in effectDivs[effectDiv].children) {
            node_name = effectDivs[effectDiv].children[knob]['nodeName'];

            if (node_name === 'H3') {
                knob_value = effectDivs[effectDiv].children[knob].innerHTML;
                console.log(knob_value);
                current_effectJson['type'] = knob_value;
            }

            if (node_name === 'INPUT') {
                knob_value = effectDivs[effectDiv].children[knob].value;
                knob_id = effectDivs[effectDiv].children[knob]['attributes']['id'].value;
                //console.log(knob_id);
                current_effectJson[knob_id.toString().toLowerCase()] = knob_value;
            }
        }
        effectsJson.push(current_effectJson);
    }
    effectsJson = effectsJson.slice(0, -3)
    effectsJson = JSON.stringify(effectsJson);
    console.log(effectsJson);
    return effectsJson;
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