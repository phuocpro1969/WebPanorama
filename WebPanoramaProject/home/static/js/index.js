let imageLists = []
let base = []
let allImage = []

function AddFile(event){
    $(document).ready(function(){
        addImage(event);
    });
}

document.getElementById("run_test").addEventListener("click", function(){
    if (base.length === 0) {
        clearImage();
        ShowAlert();
    }
});

function Image(id, name, image) {
    this.id = id;
    this.name = name;
    this.image = image;
}

function ShowAlert(){
    html = `
    <div class="alert alert-warning alert-dismissible fade show" role="alert">
        <h1><strong>WARNING!</strong> YOU MUST ADD IMAGE FIRST</h1>
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
         </button>
    </div>
    `
    document.getElementById("showAlert").innerHTML = html;
}

function renderOnlyResult(){
    html = `
        <div id="result" style="text-align: center;">
             <h1>RESULT</h1>
                 <div class="row justify-content-md-center">
                     <img class="lg-image" width="pixels" src="${imageLists[0].image}" alt="result" title="result">
                 </div>
             </div>
        </div>
    `
    document.getElementById("showAnswers").innerHTML = html;
}

function addImage(event) {
    if (window.File && window.FileList && window.FileReader) {
        let allFiles = event.target.files; //FileList object
        for (let i = 0; i < allFiles.length; i++) {
            let file = allFiles[i];
            if (!file.type.match('image')) continue;
            allImage.push(file);
        }
        showImage();
    }
    callBackend()
}

function renderHtml() {
    let htmlContent = "";
    let output = document.getElementById("listAfterAddImage");
    for (let i = 0; i < imageLists.length; i++) {
        htmlContent += `
                    <div class="col-md-2">
                        <div class="card mb-1 shadow-sm">
                            <img class="bd-placeholder-img card-img-top sm-image" src="${imageLists[i].image}" alt="${imageLists[i].name}" title="${imageLists[i].name}">
                            <button type="button" onclick='deleteImage(${imageLists[i].id})' class="btn btn-sm btn-outline-secondary">Delete</button> 
                        </div> 
                    </div>
                    `;
    }
    htmlContent += ` 
                    <div class = "col-md-3">
                        <div class = "form-group"> 
                            <input type="file" multiple class="form-control-file" id="AddFile" onchange="AddFile(event)"  name="uploadImage" accept="image/*">
                        </div> 
                    </div>
                    `
    output.innerHTML = htmlContent;
}

function asyncFunction(callback, ms) {
   setTimeout(() => {
      callback();
   }, ms);
}

function callBackend(){
    document.getElementById("run_test").addEventListener("click", function(){
        if (base.length === 1){
            document.getElementById("categories").innerHTML =`
                <a class="nav-link" href="#input">INPUT</a>
                <a class="nav-link" href="#result">RESULT</a>
                `;
            renderOnlyResult(imageLists);
        }
        if(base.length >=2) {
            document.getElementById("showAnswers").innerHTML = "";
            let csrf = $('input[name=csrfmiddlewaretoken]').val();
            $.ajax({
                url: '.',
                method: 'POST',
                dataType: 'json',
                data: {
                    base,
                    csrfmiddlewaretoken: csrf,
                },
                success: function (response, status) {
                    content = JSON.parse(response['content']);
                    renderAnswerHTML(content);
                }
            });
        }
    });
}

function showImage() {
    base = []
    imageLists = []
    for (let i = 0; i < allImage.length; i++) {
        let picReader = new FileReader();
        picReader.readAsDataURL(allImage[i]);
        picReader.addEventListener("load", function(event){
            let result = event.target.result;
            let image = new Image(Math.random(), allImage[i].name, result);
            base.push(result);
            imageLists.push(image);
        })
    }
    asyncFunction(renderHtml, 200);
}

function buildCategories(n) {
    let categoriesHTML = `
        <a class="nav-link" href="#input">INPUT</a>
    `;
    for (let i = 1; i < n; i++){
        let hr = "step_" + i;
        categoriesHTML += `
            <a class="nav-link" href="#${hr}">STEP ${i}:</a>
        `;
    }
    categoriesHTML += `
            <a class="nav-link" href="#result">RESULT</a>
        `;
    document.getElementById("categories").innerHTML = categoriesHTML;
}

function buildOutputStep(content){
    let n = base.length;
    let html = "";
    let arrKeyPoints = content['arrKeyPoints']
    let arrKeyPointsAfterCompare = content['arrKeyPointsAfterCompare']
    let arrMatcher = content['arrMatcher']
    let arrRansac = content['arrRansac']
    let arrResult = content['arrResult']
    html += `
        <div>
            <div id="step_1" style="text-align: center;">
                <h1>STEP 1: COMPARE IMAGE 1 AND IMAGE 2</h1>
            </div>
            <h2>1.1. KeyPoints<h2>
            <div class="row">
                <div class="col">
                    <img class="md-image" src="${arrKeyPointsAfterCompare[0]}" alt="keypoints image 1" title="keypoints image 1">
                </div>
                <div class="col">
                     <img class="md-image" src="${arrKeyPoints[0]}" alt="keypoints image 2" title="keypoints image 2">
                </div>
            </div>
            <h2>1.2 Matching By RANSAC</h2>
            <h3>1.2.1 Matching KeyPoint Default</h3>
            <div class="row justify-content-md-center">
                <img class="lg-image" width="pixels" src="${arrMatcher[0]}" alt="match image 1 with image 2" title="match image 1 with image 2">
            </div>
            <h3>1.2.2 Matching KeyPoints Out Image</h3>
            <div class="row justify-content-md-center">
                <img class="lg-image" width="pixels" src="${arrRansac[0]}" alt="re-match with keypoints out image" title="re-match with keypoints out image">
            </div>
            <br>    
            <h2>1.3 Result After Matching </h2>
            <div class="row justify-content-md-center">
                <img class="lg-image" width="pixels" src="${arrResult[0]}" alt="result image matched step 1" title="result image matched step 1">
            </div>
        </div>
    `

    for (let i=2; i<n; i++){
        html += `
            <div>
                <div id="step_${i}" style="text-align: center;">
                    <h1>STEP ${i}: COMPARE IMAGE ANSWERS STEP ${i - 1} AND IMAGE ${i + 1}</h1>
                </div>
                <h2>${i}.1. KeyPoints<h2>
                <div class="row">
                    <div class="col">
                        <img class="md-image" src="${arrKeyPointsAfterCompare[i-1]}" alt="keypoints image result in step ${i - 1}" title="keypoints image result in step ${i - 1}">
                    </div>
                    <div class="col">
                        <img class="md-image" src="${arrKeyPoints[i-1]}" alt="keypoints image ${i}" title="keypoints image ${i}">
                    </div>
                </div>
                <h2>${i}.2 Matching By RANSAC</h2>
                <h3>${i}.2.1 Matching KeyPoint Default</h3>
                <div class="row justify-content-md-center">
                    <img class="lg-image" width="pixels" src="${arrMatcher[i-1]}"" alt="match image result in step_${i - 1} with image ${i + 1}" title="match image result in step_${i - 1} with image ${i + 1}">
                </div>
                <h3>${i}.2.2 Matching KeyPoints Out Image</h3>
                <div class="row justify-content-md-center">
                    <img class="lg-image" width="pixels" src="${arrRansac[i-1]}" alt="re-match with keypoints out image" title="re-match with keypoints out image">
                </div>
                <br>
                <h2>${i}.3 Result after matching </h2>
                <div class="row justify-content-md-center">
                    <img class="lg-image" width="pixels" src="${arrResult[i-1]}" alt="result image step ${i}" title="result image step ${i}">
                </div>
            </div>
        `
    }

    html += `
        <div id="result" style="text-align: center;">
             <h1>RESULT</h1>
                 <div class="row justify-content-md-center">
                     <img class="lg-image" width="pixels" src="${arrResult[n-2]}" alt="result" title="result">
                 </div>
             </div>
        </div>
    `
    document.getElementById("showAnswers").innerHTML = html;
}

function renderAnswerHTML(content){
    buildCategories(base.length);
    buildOutputStep(content);
}

function findById(id, arr) {
    for (let i = 0; i <= arr.length; i++) {
        if (arr[i].id === id) {
            return i;
        }
    }
    return -1;
}

function clearImage() {
    allImage = [];
    imageLists = [];
    document.getElementById("listAfterAddImage").innerHTML = `
    <div class = "col-md-3">
        <div class = "form-group">
            <input type="file" multiple class="form-control-file" id="AddFile" name="uploadImage" onchange="AddFile(event)" accept="image/*">
        </div> 
    </div>
    `;

    base = [];
    document.getElementById("showAnswers").innerHTML = "";
    document.getElementById("categories").innerHTML = `
        <a class="nav-link" href="#input">INPUT</a>
    `;
    localStorage.clear();
}

function deleteImage(id) {
    let index = findById(id, imageLists);
    imageLists.splice(index, 1);
    base.splice(index, 1);
    allImage.splice(index, 1);
    renderHtml(imageLists);
    //saveData("base", base);
}

// function saveData(key, value) {
//     var blob = new Blob(
//         value,
//         {
//             type:"application/json;utf-8"
//         }
//     );
//     var userLink = document.createElement('a');
//     userLink.setAttribute('download', key);
//     userLink.setAttribute('href', window.URL.createObjectURL(blob));
//     userLink.click();
// }

// function fetchData(key, arr) {
//     arr=[]
//     let local = localStorage.getItem(key);
//     console.log(local);
//     if (local) {
//
//         mapData(JSON.parse(local), arr);
//         console.log(arr);
//         //renderHTML(arr);
//     } else {
//         console.log("no data");
//     }
// }
//
// function fetchBase(key, arr) {
//     arr=[]
//     let local = localStorage.getItem(key);
//     if (local) {
//         let data = JSON.parse(local);
//         for (let i = 0; i <= data.length; i++)
//             if (!!data[i])
//                 arr.push(data[i]);
//         //renderHTML(arr);
//     } else {
//         console.log("no data");
//     }
// }

// function mapData(data, arr) {
//     for (let i = 0; i < data.length; i++) {
//         let image = new Image(
//             data[i].id,
//             data[i].image
//         );
//         arr.push(image);
//     }
// }

//fetchBase("base", base);
/*fetchData("imageLists", imageLists);*/