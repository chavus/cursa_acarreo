// This function uses Android app RawBT to print ticket
// https://rawbt.ru/start.html with  rawbt:data:image/jpeg;base64,data 

function printImage(imageB64){
    window.location.href = "rawbt:data:image/jpeg;base64," + imageB64
}
 