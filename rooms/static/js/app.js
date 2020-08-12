"use strict"

// Home Page
const waypointFadeElements = document.querySelectorAll('[class*="wp-fade-"]')
if (waypointFadeElements.length > 0) {
    if (setInterval && Element.prototype.getBoundingClientRect) {
        setInterval(() => {
            for (let el of waypointFadeElements) {
                if (isElementInViewport(el.parentElement, 100, 200)) {
                    el.classList.add('wp-show')
                } else {
                    el.classList.remove('wp-show')
                }
            }
        }, 250);

    } else {
        // Callback if does not support inview script
        for (let el of waypointFadeElements) {
            el.classList.add('wp-show')
        }
    }
    
}

// Check if element in viewport, added support for offset
function isElementInViewport(el, offsetX, offsetY) {
    offsetX = offsetX || 0
    offsetY = offsetY || 0

    var rect = el.getBoundingClientRect();

    return (
        (rect.top + offsetY) >= 0 &&
        (rect.left + offsetX) >= 0 &&
        (rect.bottom - offsetY) <= (window.innerHeight || document.documentElement.clientHeight) &&
        (rect.right - offsetX) <= (window.innerWidth || document.documentElement.clientWidth)
    );
}


// CSRF Forms
const csrf_token = Cookies.get('csrftoken')
const put_options = {
    method: 'PUT',
    headers: {
        'X-CSRFToken': csrf_token
    }
}



// ----- Room Detail Page -----
const _room_detail = document.querySelector('#roomDetail')
if (_room_detail) {
    const el_roomCode = document.getElementById('roomCode')
    const el_roomCodeToggle = document.getElementById('roomCodeToggle')
    const el_roomCodeCopy = document.getElementById('roomCodeCopy')

    const roomCode = el_roomCode.innerText

    function init_roomcode() {
        el_roomCode.innerText = '*****'
        el_roomCodeToggle.addEventListener('click', () => {
            const _icon = el_roomCodeToggle.querySelector('span')
            const _hide = _icon.innerText == 'visibility'
    
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
        const _init = document.createElement('input');
        _init.type = 'text'; _init.id = 'roomCodeCopyText';
        _init.style = 'position: absolute; top: -1000px; left: -1000px;'
        _init.value = roomCode; 
        
        el_roomCodeCopy.addEventListener('click', () => {
            // append _init to body,
            document.body.appendChild(_init)
            const _placeholder = document.getElementById('roomCodeCopyText')
    
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
        const urlHash = window.location.hash
        if (urlHash != "") {
            $(`#roomTabs a[href="${urlHash}"]`).tab('show')
            window.location.hash = ''
        }
    }

    function init_roomcode_qr() {
        const qr_element = document.querySelector('#roomQR')
        // generate qrcode
        if (qr_element) {
            new QRCode(qr_element, roomCode)

            // center qr code
            const qr_img = qr_element.querySelector('img')
            qr_img.style.margin = "auto"; 

            setTimeout(() => {
                const qr_src = qr_img.src
                const downloadButton = document.querySelector('#roomQRDownload')
                downloadButton.href = qr_src
            }, 500);
            
        }
        
    }

    function initRoomDescription() {
        const room_detail_description = _room_detail.querySelector('#roomDescription')
        const room_detail_header = _room_detail.querySelector('#roomDescriptionHeader')
        const room_detail_toggle = _room_detail.querySelector('#roomDescriptionToggle')

        let description = ''
        for (let paragraphs of room_detail_description.querySelectorAll('p')) {
            console.log(room_detail_description.childNodes);
            description += paragraphs.innerText
        }

        console.log(description);

        if (description.trim() === '') {
            room_detail_header.innerText = 'No description available'
            room_detail_toggle.style.display = 'none'
        }
    }

    init_roomcode()
    init_roomcode_qr()
    show_hash_tab()
    initRoomDescription()

}



// Notifications
const _room_tabs =  document.querySelector('#roomTabs')
if (_room_tabs) {
    const tabs = _room_tabs.querySelectorAll('.nav-item > a')

    for (let tab of tabs) {
            // If tab is clicked, clear notifications
            const url = tab.getAttribute('data-seen-href')
            const _tab_id = tab.getAttribute('href')

            tab.addEventListener('click', function(event) {
                const badge = tab.querySelector('.badge')
                const badge_total_notif = document.querySelector('.badge-notification')

                if (!badge.classList.contains('d-none')) {
                    fetch(url, put_options).then(res => {
                        if (!res.ok) throw new Error('Oops! Something went wrong.')
                        return res.json().then(data => {
                            update_notif_badges(badge, data.unseen_object)
                            update_notif_badges(badge_total_notif, data.unseen_total);

                            // Remove Notification word style if no remaining notifications
                            if (data.unseen_total <= 0) remove_notification_item_style()

                            const unread_cards = document.querySelectorAll(`${_tab_id} > div .card-unread `)
                            
                            setTimeout(() => {
                                remove_unread(unread_cards)    
                            }, 2000);
                        })
                    }).catch(err => {
                        showToastError(err)
                    })
                            
                      
                }

            })
    }

}

function update_notif_badges(element, new_count) {
    if (element) {
        if (new_count <= 0) element.classList.add('d-none');
        element.innerText = new_count
    }
}

function remove_unread(elementList) {
    for (let el of elementList) {
        el.classList.remove('card-unread')
    }
}

function remove_notification_item_style() {
    const element = document.querySelector('#notificationListItem')
    if (element) {
        element.classList.remove('text-primary')
        element.classList.remove('font-weight-bold')
    }
}

// Like Button API
initLikeButtons()
function initLikeButtons() {
    const _like_buttons = document.querySelectorAll('.btn-like')
    for (let button of _like_buttons) {
        button.addEventListener('click', function(event) {
            event.preventDefault()

            const _like_url = button.href
            request_like(button, _like_url)
        })
    }
}


function request_like(element, url) {
    element.classList.add('disabled')

    fetch(url, put_options)
    .then(res => {
        if (!res.ok) {            
            throw new Error('Oops! Something went wrong.')
        } else {
            res.json().then(data => {
                update_like_button(element, data.liked, data.new_like_count)
            })
        }
    })
    .catch(err => {
        showToastError(err)
        element.classList.remove('disabled')
    })

    
}

function update_like_button(el, liked, count) {
    if (el != undefined) {
        el.querySelector('.like-count').innerText = count
        el.setAttribute('data-likes', count)

        const _icon = el.querySelector('.material-icons')
        if (liked) _icon.classList.add('text-primary')
        else  _icon.classList.remove('text-primary')

        setTimeout(() => {
            el.classList.remove('disabled');
        }, 200);
    }

}



// ----- Room Join Page -----
// QR Scanner
const roomJoinForm = document.getElementById('roomJoinForm')
const qrScannerToggle = document.getElementById('qrScannerToggle')
if (roomJoinForm && qrScannerToggle) {
    if (window.location.protocol === 'https:') {        
        const html5QrCode = new Html5Qrcode("qr-scanner");

        qrScannerToggle.addEventListener('click', (event) => {
            // Get permission and camera, then run scanner
            const constraints = {
                video : { facingMode : 'environment' }
            }
            navigator.mediaDevices.getUserMedia(constraints).then(device => {
                if (device) {
                    const rearCameraId = device.getVideoTracks()[0].getSettings().deviceId
                    runScanner(rearCameraId);
                }
            })
            .catch(err => {
                if (err.code === DOMException.NOT_FOUND_ERR) {
                    showToastError('No rear camera found.')
                } else if (err.code === DOMException.SECURITY_ERR) {
                    showToastError('Cannot access the camera.')
                }
            });
        
            $('#qrScannerModal').on('hidden.bs.modal', () => {
                try {
                    html5QrCode.stop()
                } catch (err) {
                    console.error(err);
                }
                
            })
            
            function runScanner(cameraId) {
                console.log('Running Scanner on Camera ID: ', cameraId);
                $('#qrScannerModal').modal('show')
                
                html5QrCode.start(
                cameraId, 
                {
                    fps: 10,
                    qrbox: 250
                },
                qrCodeMessage => {
                    // Hide modal, stop scanner
                    $('#qrScannerModal').modal('hide')
                    
                    // Enter code then submit
                    roomJoinForm['id_code'].value = qrCodeMessage
                    roomJoinForm.submit()
                    
                },
                errorMessage => {
                    // console.error(errorMessage);
                })
                .catch(err => {
                    showToastError(err)
                });
            }
        
        })
    } else {
        qrScannerToggle.disabled = true
    }
}



// ----- User Room Page -----

// Room Backgrounds
const roombgForm = document.querySelector('#roombgForm');
if (roombgForm) {
    const options = document.querySelectorAll('.roombg-option')

    function select_item(item) {
        for (let option of options) {
            option.classList.remove('roombg-option-selected')
        }
        item.classList.add('roombg-option-selected')
        roombgForm['room_bg_id'].value = item.getAttribute('data-bg-id')

        console.log(roombgForm['room_id'].value, roombgForm['room_bg_id'].value);
    }

    // Click event
    for (let option of options) {
        option.addEventListener('click', () => select_item(option) )
    }

    $('#roomBackgroundModal').on('show.bs.modal', function (event) {
        const button = $(event.relatedTarget)
        roombgForm['room_id'].value = button.data('room-id')

        const roombgId = button.data('room-bg');
        if (roombgId) {
            const item = document.querySelector(`[data-bg-id="${roombgId}"]`)
            select_item(item)
        }
    })
}

const _hasGradientBackgrounds = document.querySelectorAll('[data-dark-background]')
for (let element of _hasGradientBackgrounds) {
    const overlay = 'linear-gradient(rgba(0,0,0,0.6) 50%, rgba(0,0,0,0.3))'
    element.style.backgroundImage = `${overlay}, url(${element.getAttribute('data-dark-background')})`
    element.style.backgroundBlendMode = 'normal'
}

const _hasBackgrounds = document.querySelectorAll('[data-light-background]')
for (let element of _hasBackgrounds) {
    const overlay = 'linear-gradient(180deg, rgba(255,255,255,0.8) 50%, rgba(255,255,255,1) 100%)'
    element.style.backgroundImage = `${overlay}, url(${element.getAttribute('data-light-background')})`
    element.style.backgroundPosition = 'center top, 0 50%'
    element.style.backgroundBlendMode = 'normal'
    
}


// ----- All User Notifications Page -----
const readAllNotifications = document.querySelector('#readAllNotifications')
if (readAllNotifications) {
    readAllNotifications.addEventListener('click', (event) => {
        event.preventDefault()

        const count = document.querySelector('#notificationCount')

        if (count && !count.classList.contains('d-none')) {
            
            fetch(readAllNotifications.href, put_options).then(res => {
                if (!res.ok) throw new Error('Something went wrong')
                return res.json().then(data => {
                    update_notif_badges(count, data.unseen_total)
                    remove_unread(document.querySelectorAll('.card-unread'))                    
                    remove_notification_item_style()
                })
            }).catch(err => {
                showToastError(err)
            })
        }
        
    })
}



// ----- Upload File Page -----
// File Validation variables
const max_file_size_mb = 5
const max_file_size = max_file_size_mb * (1024 * 1024)
const allowed_file_types = [
    '.doc', '.docx', '.pdf', '.ppt', '.pptx'
]

// File Form
const _file_form = document.querySelector('#fileForm')
if (_file_form) {
    // limit file picker types (can be overridden)
    document.querySelector('#id_raw_file').setAttribute('accept', allowed_file_types.toString())
}



// ----- Post Announcement Page -----
// Announcement Form
const _ann_form = document.querySelector('#announcementForm')
if (_ann_form) {
    const _content = document.querySelector('#id_content')    
    if (_content != null) _content.setAttribute('placeholder', "What's on your mind?")
}




// ----- Profile Edit page -----
// Select Avatar Modal
const _input_avatar = document.querySelector('#id_avatar')
const _modal_avatar_select = document.querySelector('#avatar-select-modal')
const _selected_avatar_preview = document.querySelector('.avatar-selected-preview')
if (_input_avatar && _modal_avatar_select) {

    const _avatar_items = document.querySelectorAll('.avatar-item')
    const _avatar_select_button = document.querySelector('.btn-avatar-select')

    for (let item of _avatar_items) {
        item.addEventListener('click', function(event) {
            event.preventDefault()

            highlight_item(item)
        })
    }

    function highlight_item(element) {
        for (let item of _avatar_items) {
            item.classList.remove('avatar-item-selected')
        }
        element.classList.add('avatar-item-selected')
    }

    _avatar_select_button.addEventListener('click', function(event) {
        const _selected_avatar = document.querySelector('.avatar-item-selected')
        const _selected_avatar_image = _selected_avatar.querySelector('img')

        // Set form input-avatar value to selected-item id
        _input_avatar.value = _selected_avatar.value

        // Set modal preview image
        _selected_avatar_preview.setAttribute('src', _selected_avatar_image.src)
        _selected_avatar_preview.setAttribute('alt', _selected_avatar_image.alt)
    })

}



const _countdown = document.querySelector('.countdown')
// Close Account Page
const _close_account = document.querySelector('#closeAccount')

if (_countdown && _close_account) {
    // init
    let duration = parseInt(_countdown.getAttribute("data-duration"))
    _countdown.innerText = `(${duration}s)`

    // set timeout clear disable
    setTimeout(() => {
        _close_account.disabled = false
    }, duration*1000);

    // change timer text, 
    const timer = setInterval(() => {
        duration -= 1
        _countdown.innerText = `(${duration}s)`
        
        if (duration <= 0) {
            clearInterval(timer)
            _countdown.innerText = ''
        }
        
    }, 1000);

}



// --- Room People page -----
// Ban modal
const banForm = document.getElementById('banForm')
if (banForm) {
    $('#banModal').on('show.bs.modal', function (event) {

        const button = $(event.relatedTarget)
        const userId = button.data('user-id')
        const username = button.data('username')
        const banStatus = button.data('ban-status')
        
        if (banStatus === 'True') {
            $('#banModal .modal-title').text(`Unban user in your room?`)
            $('#banModal .modal-body p').html(`Are you sure you want to unban <strong>${username}</strong>?`)
            banForm['ban_user'].innerText = 'Yes, Remove Ban'
        } else {
            $('#banModal .modal-title').text(`Ban user in your room?`)
            $('#banModal .modal-body p').html(`Are you sure you want to ban <strong>${username}</strong>?`)
            banForm['ban_user'].innerText = 'Yes, Ban User'
        }
        
        banForm['ban_user'].value = userId
    })
}



// ----- Global ------
// Clear Search buttons
const _links_clear_search = document.querySelectorAll('.btn-search-cancel')
if (_links_clear_search != null) {
    for (let l of _links_clear_search) {
        const params = new URL(location.href).searchParams
        if (
            !params.get('search') &&
            !params.get('sort')
        ) { l.style.display = 'none' }
    }
}

// Infinite Container Loading Script
const _infinite_items = document.querySelector('.infinite-container')
if (_infinite_items) {
    const loadingModal = $('#loadingModal')
    let loading = false
    let loaded = false

    const longLoadingTime = 1000
    const modalTimeout = 5000
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
            const currTime = (new Date()).getMilliseconds()
            const timeDiff = currTime - startTime

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

// Border
initBorder()
function initBorder() {
    const avatarContainers = document.querySelectorAll('.avatar-container')
    for (let avatar of avatarContainers) {
        const borderSrc = avatar.getAttribute('data-border')
        if (borderSrc) {
            avatar.style.backgroundImage = `url(${borderSrc})`
        }                                
    }
}

// Room Description Collapsible Container
const collapsibleContainerToggles = document.querySelectorAll('.collapsible-toggle')
if (collapsibleContainerToggles) {
    for (let toggle of collapsibleContainerToggles) {
        toggle.addEventListener('click', function () {
            const containerId = toggle.getAttribute('data-collapse-target')
            const isCollapsed = document.querySelector(containerId).classList.toggle('collapsed-container')
            if (isCollapsed) {
                toggle.querySelector('span').style.transform = 'rotate(180deg)'
            } else {
                toggle.querySelector('span').style.transform = 'rotate(0)'
            }
            
        })
    }
}

// Check browser if supports window fetch
if (!window.fetch) {
    const messages = document.querySelector('#messages')

    const alert = document.createElement('div')
    alert.classList.add('alert', 'alert-danger', 'small')
    alert.innerHTML =
    `<strong>Please use other browsers such as Chrome or Firefox</strong>. \
    Your browser isn't fully supported as of the moment. \
    You may still continue to use the site, but some functions may not work.`
    
    messages.appendChild(alert)
}



// ----- Functions ------

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
    const file_type = _selected_file.name.match(/\.([0-9a-z]+)$/)[0]
    const file_size = _selected_file.size

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
        let _errors = _parent.querySelectorAll('.invalid-feedback')
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

function showToastError(message) {
    // init error toast
    $.snackbar({ content:message, style:'toast', timeout:2000})
}
