if (document.querySelector('#roomDetailID') != null) {
    let el_roomCode = document.getElementById('roomCode')
    let el_roomCodeToggle = document.getElementById('roomCodeToggle')
    let el_roomCodeCopy = document.getElementById('roomCodeCopy')

    let roomCode = el_roomCode.innerText
    
    el_roomCodeToggle.addEventListener('click', () => {
        _hide = el_roomCode.getAttribute('data-hide') == 'true'
    
        if (_hide) {
            el_roomCode.innerText = roomCode
            el_roomCodeToggle.querySelector('use').setAttribute('xlink:href', "/static/icons/hide.svg#fill")
            el_roomCode.setAttribute('data-hide', 'false')
        } else {
            el_roomCode.innerText = '*****'
            el_roomCodeToggle.querySelector('use').setAttribute('xlink:href', "/static/icons/show.svg#fill")
            el_roomCode.setAttribute('data-hide', 'true')
        }
    })
    el_roomCodeToggle.click()

    // Init input element for code copy
    let _init = document.createElement('input');
    _init.type = 'text'; _init.id = 'roomCodeCopyText';
    _init.style = 'position: absolute; top: -1000px; left: -1000px;'
    _init.value = roomCode; 
    
    el_roomCodeCopy.addEventListener('click', () => {
        // append _init to body,
        document.body.appendChild(_init)
        let _placeholder = document.getElementById('roomCodeCopyText')

        // copy the value (code)
        _placeholder.select();
        _placeholder.setSelectionRange(0, 99999);
        document.execCommand('copy')

        // then remove element
        _placeholder.remove()
    })
}
