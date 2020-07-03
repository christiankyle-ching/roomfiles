if (document.querySelector('#roomDetailID') != null) {
    let el_roomCode = document.getElementById('roomCode')
    let el_roomCodeToggle = document.getElementById('roomCodeToggle')
    let el_roomCodeCopy = document.getElementById('roomCodeCopy')

    let roomCode = el_roomCode.innerText
    
    el_roomCode.innerText = '*****'
    el_roomCodeToggle.addEventListener('click', () => {
        _icon = el_roomCodeToggle.querySelector('span')
        _hide = _icon.innerText == 'visibility'

        if (_hide) {
            // if hidden, then show
            el_roomCode.innerText = roomCode
            _icon.innerText = 'visibility_off'
        } else {
            // if shown, then hide
            el_roomCode.innerText = '*****'
            _icon.innerText = 'visibility'
        }
    })

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
