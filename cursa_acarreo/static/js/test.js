// var Fraction = require('fractional').Fraction
import { Fraction } from 'fractional'
import {elements} from './test_el'

function convert(){
    // elements.test_display.textContent = elements.test_input.value
    elements.test_display.textContent = (new Fraction(0.35))
}

elements.test_btn.addEventListener('click', convert)