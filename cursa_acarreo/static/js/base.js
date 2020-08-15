// const elements = {

// };

const elementsString = {
    loader: 'loader'
};


function displayLoader(parent, text='', size='sm', position='inner'){
    // position = 'inner', 'afterbegin', 'beforeend'
    const sizeRem = size === 'lg' ? '1.5' : '1' 

    markup = ` 
    <div>
        <span class="spinner-border ${elementsString.loader}" style="width: ${sizeRem}rem; height: ${sizeRem}rem;" role="status" aria-hidden="true"></span>
        <span class=${elementsString.loader}>   ${text}</span>
    </div>
    `
    if (position === 'inner'){
        parent.innerHTML = markup
    }else{
        parent.insertAdjacentHTML(position, markup)
    }
    
}

function clearLoader(){
    const loaderList = document.querySelectorAll(`.${elementsString.loader}`)
    loaderList.forEach((el) => el.parentElement.removeChild(el))
}