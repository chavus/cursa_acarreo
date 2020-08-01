// export const elements = {

// };

const elementsString = {
    innerLoader: 'innerLoader'
};


function displayInnerLoader(parent, text, size='sm'){
    const sizeRem = size === 'lg' ? '1.5' : '1' 

    markup = ` 
        <span class="spinner-border ${elementsString.innerLoader}" style="width: ${sizeRem}rem; height: ${sizeRem}rem;" role="status" aria-hidden="true"></span>
        <span>   ${text}</span>
    `
    console.log(parent)
    console.log(markup);
    parent.innerHTML = markup
}

function clearInnerLoader(){
    const loader = document.querySelector(`.${elementsString.innerLoader}`)
    if (loader) loader.parentElement.removeChild(loader)
}