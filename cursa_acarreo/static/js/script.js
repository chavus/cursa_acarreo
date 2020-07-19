import  { elements } from './base.js';
console.log('New console log... Hello from script2.js')

console.log('Hello from script5.js')
//alert('Loading script.js')

function sendUrlToPrint(){
    var url = 'https://cursa-acarreo-dev.herokuapp.com/test.pdf'
    var  beforeUrl = 'intent:';
    var  afterUrl = '#Intent;';
    // Intent call with component
    afterUrl += 'component=ru.a402d.rawbtprinter.activity.PrintDownloadActivity;'
    afterUrl += 'package=ru.a402d.rawbtprinter;end;';
    //alert(beforeUrl+encodeURI(url)+afterUrl)
    document.location=beforeUrl+encodeURI(url)+afterUrl;
    return false;
}

function printF(){
    // alert("Alerta!!")
    var S = "#Intent;scheme=rawbt;";
    var P =  "package=ru.a402d.rawbtprinter;end;";
    var textEncoded = encodeURI("Helloou");
    window.location.href="intent:"+textEncoded+S+P;
}


elements.alertButton.addEventListener('click', sendUrlToPrint)