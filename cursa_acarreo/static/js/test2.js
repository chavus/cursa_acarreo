// var Fraction = require('fractional').Fraction
// import { Fraction } from 'fractional'
// import {elements} from './test_el'

const elements = {
    test_btn: document.querySelector('#test-btn2'),
    test_input: document.querySelector('#decimal-input2'),
    test_display: document.querySelector('#fraction-display2')
}

function convert(){
    elements.test_display.textContent = elements.test_input.value
    // elements.test_display.textContent = (new Fraction(0.35))
}

elements.test_btn.addEventListener('click', convert)