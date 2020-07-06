"use strict"

// Room Detail Script
var _room_detail = document.querySelector('#roomDetailID')
if (_room_detail != null) {

    function init_roomcode() {
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

    function show_hash_tab() {
        // Select tab if hash is available
        if (window.location.hash != "") {
            $(`#roomTabs a[href="${window.location.hash}"]`).tab('show')
            window.location.hash = ''
        }
    }

    init_roomcode()
    show_hash_tab()

}

const max_file_size_mb = 5
const max_file_size = max_file_size_mb * (1024 * 1024)
const allowed_file_types = [
    '.doc', '.docx', '.pdf', '.ppt', '.pptx'
]

// File Form Script
var _file_form = document.querySelector('#fileForm')
if (_file_form != null) {
    // limit file picker types (can be overridden)
    document.querySelector('#id_raw_file').setAttribute('accept', allowed_file_types.toString())
}

// Announcement Form Script
var _ann_form = document.querySelector('#announcementForm')
if (_ann_form != null) {
    let _content = document.querySelector('#id_content')    
    if (_content != null) _content.setAttribute('placeholder', "What's on your mind?")
}

// Infinite Container Loading Script
let _infinite_items = document.querySelector('.infinite-container')
if (_infinite_items != null) {
    let loadingModal = $('#loadingModal')
    let loading = false
    let loaded = false

    let longLoadingTime = 1000
    let modalTimeout = 5000
    let timerStarted = false
    let startTime

    // Every 10ms
    setInterval(() => {
        // Update loading
        loading = _infinite_items.classList.contains('infinite-loading')

        if (loading) {
            // get start loading time if timer not yet started
            if (!timerStarted) {
                startTime = (new Date()).getMilliseconds();
                timerStarted = true;
            }
            let currTime = (new Date()).getMilliseconds()
            let timeDiff = currTime - startTime

            // If loading takes too long, then show loadingModal
            if (timeDiff > longLoadingTime) {
                // if not yet loaded, show. Else, don't do anything
                if (!loaded) loadingModal.modal('show')
            }
            
        }
    }, 10);

    // On modal show
    loadingModal.on('show.bs.modal', function () {
        // prevent trigger modal.show
        loaded = true

        // delay hide
        setTimeout(() => {
            loadingModal.modal('hide')
        }, modalTimeout);
    })

    // On modal hide
    loadingModal.on('hidden.bs.modal', function () {
        loaded = false
    })
}

// Functions

/**
 * 
 * @param {string} el_id The 'id' attribute of the input[type='file']
 * @param {string} type 'file' or 'image'. Used to have different type of checks to be done.
 */
function checkFile(el_id, type) {
    // get input[file] and its parent
    let _fileEl = document.querySelector(`#${el_id}`)
    let _parent = _fileEl.parentElement

    clearErrors()

    // get the selectedfile
    let _selected_file = _fileEl.files[0]

    // if no selected file, return
    if (_selected_file == undefined) return
    
    // get file_type(string) and file_size(int)
    let file_type = _selected_file.name.match(/\.([0-9a-z]+)$/)[0]
    let file_size = _selected_file.size

    // if file_type has no file extension, don't check for size or if allowed_type
    if (file_type == null) showError('Invalid file type.')
    else {

        // if it is file, do checks for files
        if (type == 'file') {

            if (allowed_file_types.includes(file_type) && file_size <= max_file_size) {
                // if passes tests, then return true to proceed to server upload
                return true
            } else {
                if (!allowed_file_types.includes(file_type)) showError(`Unsupported file type. File type can only be ${allowed_file_types.toString()}`);
                if (file_size >= max_file_size) showError(`File size must not exceed ${max_file_size_mb}MB.`);
            }
            
        // else, do checks for image
        } else if (type == 'image') {

        }

    }

    // return false if errors are found
    return false

    function clearErrors() {
        _errors = _parent.querySelectorAll('.invalid-feedback')
        for (let e of _errors) e.remove()
    }

    function showError(error_message) {
        let _error = document.createElement('p')
        let _errorText = document.createElement('strong')
        _errorText.innerText = error_message

        _error.classList.add('invalid-feedback')
        _error.appendChild(_errorText)
        
        _parent.appendChild(_error)
    }
}

var _links_no_search = document.querySelectorAll('.link-no-search')
if (_links_no_search != null) {
    for (let l of _links_no_search) {
        let _link = new URL(window.location)
        _link.search = ''
        l.href = _link.toString()
    }
}


