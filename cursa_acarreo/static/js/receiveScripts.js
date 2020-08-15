// ReceiveScripts.js

const ReceiveCtrl = () => {

    const RECEIVE_URL = '/receive';
    const TRIP_INFO_URL = '/_get_trip_info'
    const BACK_CAMERAS_LABELS = ['back', 'trasera']
    let qrScanner = undefined;

    const elementsId = {
        receiveModalId: 'receive-confirmation-modal'
    };

    const receiveElements = {
        receiveScanBtn: document.querySelector('#receive-scan-btn'),
        receiveCancelScanBtn: document.querySelector('#cancel-scan-btn'),
        receiveCompleteTripBtns: document.querySelectorAll('.receive-complete-button'),
        receiveCancelTripBtns: document.querySelectorAll('.receive-cancel-button'),
        confirmationModal: document.querySelector(`#${elementsId.receiveModalId}`),
        receiveModalHeader: document.querySelector('#receive-modal-header'),
        receiveModalTruck: document.querySelector('#receive-modal-truck'),
        receiveModalOrigin: document.querySelector('#receive-modal-origin'),
        receiveModalMaterial: document.querySelector('#receive-modal-material'),
        receiveModalDestination: document.querySelector('#receive-modal-destination'),
        receiveModalComment: document.querySelector('#receive-modal-comment'),
        receiveModalCompleteBtn: document.querySelector('#receive-modal-complete-btn'),
        receiveModalCancelIcon: document.querySelector('#cancel-icon-p'),
        receiveModalCloseBtn: document.querySelector('#receive-modal-close')
    };

    function _containsBackLabel(label){ 
        // Returns true if label of camera contains BACK_CAMERAS_LABELS 
        for (i=0; i<BACK_CAMERAS_LABELS.length; i++){ 
            if (label.toLowerCase().includes(BACK_CAMERAS_LABELS[i])){
                return(true)
            } 
        }
    }

    async function getCamera() {
        let cameraId = undefined;
        await Html5Qrcode.getCameras().then(devices => {
            if (devices){
                alert('IN devices')
                // alert(`# of cameras: ${devices.length}\n
                    //  labels of cameras: ${String(devices.flatMap(d => d.label))}\n
                    //  ids of cacmeras: ${String(devices.flatMap(d => d.id))}`)
                

                // Only one camera
                if (devices.length === 1){ 
                    alert(`In Device lenght 1, showing ${devices[0].id}`);
                    cameraId = devices[0].id; } 
                // More than one camera
                else { 
                    alert('IN else');
                    // Filter labels with "back" words
                    const backCamList = devices.filter(d => _containsBackLabel(d.label)); 
                    // Show first camera with label "back"                  
                    if (backCamList){ 
                        alert(`In backCamLists, showing ${backCamList[0].id}`);
                        cameraId = backCamList[0].id;}
                    // If none, show camera [1], typically back camera                   
                    else { 
                        alert(`In none, showing ${devices[0].id}`);
                        cameraId = devices[0].id;}
                } 
            } else{
                swal('No se encontró cámara','Intente recibir viaje manualmente','error')
            }
        }).catch( err =>{
            console.log(err);
            swal('Error', err.message, 'error')
        });
        return(cameraId);
    }
    
    function scanTicket(cameraId) {
        return new Promise((resolve, reject) =>{
            const FPS = 20;
            const QRBOX = 250;
            const READER_ELEMENT = 'qr-reader'
            qrScanner = new Html5Qrcode(READER_ELEMENT);
            qrScanner.start(
            cameraId, 
            {
                fps: FPS,    // Optional frame per seconds for qr code scanning
                qrbox: QRBOX  // Optional if you want bounded box UI
            },
            qrCodeMessage => {
                resolve(qrCodeMessage);
            },
            errorMessage => {
                // Too much verbose
            })
            .catch(err => {
                console.log(err);
            });
            })
    }

    function _showConfimationModal(tripInfo, status='complete'){
        return new Promise((resolve, reject)=>{
            if (status === 'canceled'){
                receiveElements.receiveModalHeader.textContent = 
                    `¿Seguro que desea cancelar viaje: #${tripInfo._id} ?`
                receiveElements.receiveModalCompleteBtn.setAttribute(
                    "style","background-color: #dc3545; border-color: #dc3545; color: white");
                receiveElements.receiveModalCompleteBtn.textContent = 'Cancelar Viaje';
                receiveElements.receiveModalCancelIcon.removeAttribute('hidden');
            }else{ // Complete
                receiveElements.receiveModalHeader.textContent = 
                    `Recibir viaje: #${tripInfo._id}`
                receiveElements.receiveModalCompleteBtn.setAttribute(
                        "style","background-color: #007bff; border-color: #007bff; color: white");
                receiveElements.receiveModalCompleteBtn.textContent = 'Recibir Viaje'
                receiveElements.receiveModalCancelIcon.setAttribute('hidden', 'hidden')
            }
            receiveElements.receiveModalOrigin.textContent = 
                tripInfo.origin;
            receiveElements.receiveModalMaterial.textContent = 
                tripInfo.material;
            receiveElements.receiveModalDestination.textContent = 
                tripInfo.destination;
            receiveElements.receiveModalTruck.textContent = 
                tripInfo.truck;
            $(`#${elementsId.receiveModalId}`).modal('show') // jQuery due to Bootstrap
    
            receiveElements.receiveModalCompleteBtn.
                addEventListener('click', ()=> 
                    resolve({resp: 'ok', comment: document.querySelector('#receive-modal-comment') ? document.querySelector('#receive-modal-comment').value: ''
                }))
            receiveElements.receiveModalCloseBtn.
                addEventListener('click', ()=>
                    resolve({resp: 'cancel'}))
                })
    }

    async function finalizeTrip(tripId, status, comment='') {
        try{
            const ret = await axios.post(RECEIVE_URL, {
                trip_id: tripId,
                status: status,
                finalizer_comment: comment
            });
            swal(ret.data.message,'', 'success').then(()=>{
                // cancelScanTrip();
                location.reload()});
        }catch(error){
            console.log(error.response);
            let errorMsg = undefined;
            let type = 'error';
            if (error.response.status === 409 && error.response.data.message){
                errorMsg = error.response.data.message
                type = 'warning'
            }else if (error.response.data.error){
                errorMsg = error.response.data.error
            }else{
                errorMsg = error.response.statusText
            }
            swal(errorMsg,'', type).then(()=>{
                // cancelScanTrip();
                location.reload()})
        }
    };

    async function confirmReception(tripId, status='complete', scanning=true){
        // status = ['complete', 'canceled']
        try{
            let tripInfo = (await axios.get(TRIP_INFO_URL, {params: {trip_id: tripId}})).data;
            if (tripInfo.status === 'in_progress'){
                await _showConfimationModal(tripInfo, status).then(async (ret)=>{
                    if (ret.resp === 'ok'){
                        receiveElements.receiveModalCompleteBtn.setAttribute('disabled','disabled')
                        receiveElements.receiveModalCloseBtn.setAttribute('disabled','disabled')
                        displayLoader(receiveElements.receiveModalCompleteBtn,
                            ' ', 'lg')
                        await finalizeTrip(tripId, status, ret.comment)
                        clearLoader()
                        $(`#${elementsId.receiveModalId}`).modal('hide')

                    }else if(ret.resp === 'cancel' && scanning){
                        receiveTrip();
                    }
                })
            }else{
                const status_translation = {'complete': 'COMPLETO', 'canceled': 'CANCELADO'}
                swal(`Viaje ${tripInfo._id} con camión ${tripInfo.truck} ya había sido completado con estatus: ${status_translation[tripInfo.status]}!`, '', 'warning').then(()=> {
                    // cancelScanTrip();
                    if (scanning) {receiveTrip()}})
            }   
        }catch(error){
            console.log(error);
            let errorMsg = undefined;
            if (error.response.data.error){
                errorMsg = error.response.data.error
            }else{
                errorMsg = error.response.statusText
            }
            swal(errorMsg,'', 'error').then(()=>{
                // cancelScanTrip();
                location.reload()})
        }
    }

    function cancelScanTrip(){
        receiveElements.receiveScanBtn.removeAttribute('hidden');
        receiveElements.receiveScanBtn.removeAttribute('disabled');
        receiveElements.receiveCancelScanBtn.setAttribute('hidden','hidden')
        if (qrScanner) { qrScanner.stop().then(ignore => {
                //ignore
            }).catch(err=>console.log(err))
        }
    }

    async function receiveTrip() {
        try{
            receiveElements.receiveScanBtn.
                setAttribute('disabled', 'disabled')
            // 1.- Identify cam ID
            // let cameraId = localStorage.cameraId; // Check if there is camera saved
            // if (!cameraId){
                cameraId = await getCamera();
                // localStorage.setItem('cameraId', cameraId)
            // }
            receiveElements.receiveScanBtn.
                setAttribute('hidden', 'hidden')
            receiveElements.receiveCancelScanBtn.removeAttribute('hidden')
            // 2.- Start Camera and get scanned trip
            let tripId = await scanTicket(cameraId)
            cancelScanTrip()
            // 3.- Confirm trip (and Complete)
            await confirmReception(tripId)
        }catch(error){
            console.log(error);
            if (qrScanner){qrScanner.stop()}
            swal('Error', error.message, 'error')
        }
    };
     
    return {
        receiveTrip,
        receiveElements,
        cancelScanTrip,
        confirmReception
    }
 
};

receiveCtrl = ReceiveCtrl()

receiveCtrl.receiveElements.receiveScanBtn.
    addEventListener('click',()=>{
    receiveCtrl.receiveTrip();
})

receiveCtrl.receiveElements.receiveCancelScanBtn.
    addEventListener('click', ()=>{
    receiveCtrl.cancelScanTrip();
})

receiveCtrl.receiveElements.receiveCompleteTripBtns.
    forEach(el =>{
        el.addEventListener('click', click => {
        receiveCtrl.confirmReception(click.target.value, 'complete', false)
    })
})

receiveCtrl.receiveElements.receiveCancelTripBtns.
    forEach(el =>{
        el.addEventListener('click', click => {
        receiveCtrl.confirmReception(click.target.value, 'canceled', false)
    })
})

// var testBtn = document.getElementById('test-btn');
// testBtn.addEventListener('click', ()=>{
//     receiveCtrl.confirmReception(92, 'canceled', false)
// })

// Cases:
// Scanning
// 1.- Try to received cancelled or completed trip: PASSED
// 2.- Cancel on confirmation: PASSED
// 3.- Scan and complete with comment: PASSED

// Manually:
// Cancel
// 1.- Try to received cancelled or completed trip: passed
// 2.- Cancel on confirmation: PASSED
// 3.- Scan and complete with comment: PASSED

// Receive
// 1.- Try to received cancelled or completed trip: PASSED
// 2.- Cancel on confirmation: PASSED
// 3.- Scan and complete with comment: PASSED