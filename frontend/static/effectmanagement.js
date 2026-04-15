function createEffectDom(effect) {
    effectJson = JSON.parse(effect.replace(/'/g, '"'))
    const container = document.getElementById('effect-container')
    const effectElement = document.createElement('div');
    effectElement.classList.add('effect-element');
    container.appendChild(effectElement);
    for (knob in effectJson['properties']) {

        const slider = document.createElement('input');
        const def_val = effectJson['properties'][knob]['default'];
        const knob_title = effectJson['properties'][knob]['title'];

        //console.log(effectJson['properties'][knob]);
        if (effectJson['properties'][knob]['type'] === 'string') {
            effectElement.innerHTML = `<h3>${effectJson['properties'][knob]['default']}</h3>`
        }
        if (effectJson['properties'][knob]['type'] === 'number') {
            // Slider configuration
            slider.type = 'range';
            slider.step = 0.01;
            slider.min = 0;
            slider.max = def_val*10;
            slider.value = def_val;
            slider.id = knob_title;
            effectElement.appendChild(slider);

            // Label configuration
            const label = document.createElement('label');
            label.setAttribute('for', knob_title);
            label.innerHTML = knob_title
            label.innerHTML = ' ' + slider.value + ' ' + knob_title
            effectElement.appendChild(label);
            slider.addEventListener('click',function(){
                label.innerHTML = ' ' + slider.value + ' ' + knob_title
            })
        }
        if (effectJson['properties'][knob]['type'] === 'integer') {
            // Slider configuration
            slider.type = 'range';
            slider.step = 1;
            slider.min = 0;
            slider.max = def_val*10;
            slider.value = def_val;
            slider.id = knob_title;
            effectElement.appendChild(slider);

            // Label configuration
            const label = document.createElement('label');
            label.setAttribute('for', knob_title);
            label.innerHTML = ' ' + slider.value + ' ' + knob_title
            effectElement.appendChild(label);
            slider.addEventListener('click',function(){
                label.innerHTML = ' ' + slider.value + ' ' + knob_title
            })
        }

        effectElement.appendChild(document.createElement('br'));
    }

}

const effectForm = document.querySelector("#effect-form");
effectForm.addEventListener("submit", (event) => {
    event.preventDefault();
    //console.log(effectForm[0].value);
    createEffectDom(effectForm[0].value);
});