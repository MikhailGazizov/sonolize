/**
 * effectmanagement.js
 * Handles rendering of audio effect pedal cards with:
 *  - Circular SVG knobs (drag to adjust)
 *  - Delete button to remove a pedal
 *  - Arrow buttons to reorder pedals in the chain
 */

// ─── Knob Constants ──────────────────────────────────────────────────────────

const KNOB_RADIUS = 36;          // px, SVG circle radius
const KNOB_MIN_ANGLE = -135;     // degrees (7 o'clock position)
const KNOB_MAX_ANGLE = 135;      // degrees (5 o'clock position)

// ─── Circular Knob Factory ───────────────────────────────────────────────────

/**
 * Creates an SVG circular knob element.
 *
 * @param {string} id       - Unique id for the associated hidden <input>.
 * @param {number} min      - Minimum value.
 * @param {number} max      - Maximum value.
 * @param {number} step     - Step increment.
 * @param {number} value    - Initial value.
 * @returns {{ wrapper: HTMLElement, hiddenInput: HTMLInputElement }}
 */
function createKnob(id, min, max, step, value) {
    const wrapper = document.createElement('div');
    wrapper.classList.add('knob-wrapper');

    // Hidden input keeps the real value so formsubmission.js can read it
    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.id = id;
    hiddenInput.value = value;
    wrapper.appendChild(hiddenInput);

    // SVG knob
    const size = KNOB_RADIUS * 2 + 16; // canvas size with padding
    const cx = size / 2;
    const cy = size / 2;
    const r = KNOB_RADIUS;

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', size);
    svg.setAttribute('height', size);
    svg.classList.add('knob-svg');
    svg.setAttribute('role', 'slider');
    svg.setAttribute('aria-valuemin', min);
    svg.setAttribute('aria-valuemax', max);
    svg.setAttribute('aria-valuenow', value);
    svg.setAttribute('tabindex', '0');

    // Track arc (background)
    const trackArc = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    trackArc.setAttribute('cx', cx);
    trackArc.setAttribute('cy', cy);
    trackArc.setAttribute('r', r);
    trackArc.classList.add('knob-track');
    svg.appendChild(trackArc);

    // Value indicator line (the "dot" on the knob face)
    const indicator = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    indicator.classList.add('knob-indicator');
    svg.appendChild(indicator);

    // Outer ring highlight
    const ring = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    ring.setAttribute('cx', cx);
    ring.setAttribute('cy', cy);
    ring.setAttribute('r', r);
    ring.classList.add('knob-ring');
    svg.appendChild(ring);

    wrapper.appendChild(svg);

    // Value display label
    const valueLabel = document.createElement('span');
    valueLabel.classList.add('knob-value-label');
    valueLabel.textContent = Number(value).toFixed(step < 1 ? 2 : 0);
    wrapper.appendChild(valueLabel);

    // ── Internal state ────────────────────────────────────────────────────────
    let currentValue = parseFloat(value);
    let dragging = false;
    let startY = 0;
    let startValue = currentValue;

    /**
     * Maps a value to a rotation angle in degrees.
     * @param {number} v
     * @returns {number}
     */
    function valueToAngle(v) {
        const ratio = (v - min) / (max - min);
        return KNOB_MIN_ANGLE + ratio * (KNOB_MAX_ANGLE - KNOB_MIN_ANGLE);
    }

    /**
     * Redraws the indicator line based on the current value.
     */
    function render() {
        const angle = valueToAngle(currentValue);
        const rad = (angle - 90) * (Math.PI / 180);
        const innerR = r * 0.45;
        const outerR = r * 0.80;
        indicator.setAttribute('x1', cx + innerR * Math.cos(rad));
        indicator.setAttribute('y1', cy + innerR * Math.sin(rad));
        indicator.setAttribute('x2', cx + outerR * Math.cos(rad));
        indicator.setAttribute('y2', cy + outerR * Math.sin(rad));

        hiddenInput.value = currentValue;
        svg.setAttribute('aria-valuenow', currentValue);
        valueLabel.textContent = Number(currentValue).toFixed(step < 1 ? 2 : 0);
    }

    /**
     * Clamps a value within [min, max] and snaps to step.
     * @param {number} v
     * @returns {number}
     */
    function clamp(v) {
        const snapped = Math.round((v - min) / step) * step + min;
        return Math.min(max, Math.max(min, snapped));
    }

    // ── Drag interaction ──────────────────────────────────────────────────────

    svg.addEventListener('mousedown', (e) => {
        dragging = true;
        startY = e.clientY;
        startValue = currentValue;
        document.body.style.cursor = 'ns-resize';
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (!dragging) return;
        // Drag upward → increase value. Sensitivity: full drag range = (max-min)/px_per_unit
        const pxPerUnit = 200 / (max - min);
        const delta = -(e.clientY - startY) / pxPerUnit;
        currentValue = clamp(startValue + delta);
        render();
    });

    document.addEventListener('mouseup', () => {
        if (dragging) {
            dragging = false;
            document.body.style.cursor = '';
        }
    });

    // Touch support
    svg.addEventListener('touchstart', (e) => {
        dragging = true;
        startY = e.touches[0].clientY;
        startValue = currentValue;
        e.preventDefault();
    }, { passive: false });

    document.addEventListener('touchmove', (e) => {
        if (!dragging) return;
        const pxPerUnit = 200 / (max - min);
        const delta = -(e.touches[0].clientY - startY) / pxPerUnit;
        currentValue = clamp(startValue + delta);
        render();
    });

    document.addEventListener('touchend', () => { dragging = false; });

    // Keyboard support (arrow keys)
    svg.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowUp' || e.key === 'ArrowRight') {
            currentValue = clamp(currentValue + step);
            render();
            e.preventDefault();
        } else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') {
            currentValue = clamp(currentValue - step);
            render();
            e.preventDefault();
        }
    });

    // Initial render
    render();

    return { wrapper, hiddenInput };
}

// ─── Pedal Card Factory ───────────────────────────────────────────────────────

/**
 * Creates a complete pedal DOM element from an effect JSON object.
 *
 * @param {Object} effectJson - Parsed effect schema object.
 */
function createEffectDom(effect) {
    const effectJson = JSON.parse(effect.replace(/'/g, '"'));
    const container = document.getElementById('effect-container');

    const card = document.createElement('div');
    card.classList.add('effect-element');

    // ── Card header (title + controls) ────────────────────────────────────────
    const header = document.createElement('div');
    header.classList.add('pedal-header');

    const title = document.createElement('h3');
    title.classList.add('pedal-title');

    const moveLeft = document.createElement('button');
    moveLeft.classList.add('pedal-btn', 'pedal-btn--move');
    moveLeft.title = 'Move left';
    moveLeft.innerHTML = '&#8592;';
    moveLeft.addEventListener('click', () => {
        const prev = card.previousElementSibling;
        if (prev) container.insertBefore(card, prev);
    });

    const moveRight = document.createElement('button');
    moveRight.classList.add('pedal-btn', 'pedal-btn--move');
    moveRight.title = 'Move right';
    moveRight.innerHTML = '&#8594;';
    moveRight.addEventListener('click', () => {
        const next = card.nextElementSibling;
        if (next) container.insertBefore(next, card);
    });

    const deleteBtn = document.createElement('button');
    deleteBtn.classList.add('pedal-btn', 'pedal-btn--delete');
    deleteBtn.title = 'Remove pedal';
    deleteBtn.innerHTML = '&#10005;';
    deleteBtn.addEventListener('click', () => {
        card.remove();
    });

    header.appendChild(moveLeft);
    header.appendChild(title);
    header.appendChild(moveRight);
    header.appendChild(deleteBtn);
    card.appendChild(header);

    // ── Knobs area ────────────────────────────────────────────────────────────
    const knobsRow = document.createElement('div');
    knobsRow.classList.add('knobs-row');

    for (const knob in effectJson['properties']) {
        const prop = effectJson['properties'][knob];
        const defVal = prop['default'];
        const knobTitle = prop['title'];

        if (prop['type'] === 'string') {
            title.textContent = defVal;
        }

        if (prop['type'] === 'number' || prop['type'] === 'integer') {
            const step = prop['type'] === 'integer' ? 1 : 0.01;
            const min = 0;
            const max = defVal * 10;

            const knobGroup = document.createElement('div');
            knobGroup.classList.add('knob-group');

            const nameLabel = document.createElement('span');
            nameLabel.classList.add('knob-name-label');
            nameLabel.textContent = knobTitle;

            const { wrapper } = createKnob(knobTitle, min, max, step, defVal);

            knobGroup.appendChild(wrapper);
            knobGroup.appendChild(nameLabel);
            knobsRow.appendChild(knobGroup);
        }
    }

    card.appendChild(knobsRow);
    container.appendChild(card);
}

// ─── Form listener ────────────────────────────────────────────────────────────

const effectForm = document.querySelector('#effect-form');
effectForm.addEventListener('submit', (event) => {
    event.preventDefault();
    createEffectDom(effectForm[0].value);
});