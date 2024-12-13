async function uploadFileAndConvert() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('http://localhost:8000/convert_to_excel/', {
            method: 'POST',
            body: formData
        });

        console.log('Response status:', response.status);

        if (response.ok) {
            // If the response is successful, trigger the file download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = 'file.xlsx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);

            // Display conversion result
            const resultSection = document.getElementById("resultSection");
            resultSection.style.display = "block";
            resultSection.querySelector("#excelFile").textContent = "Excel file downloaded successfully";

            // Display download button
            const downloadButton = document.getElementById("downloadButton");
            downloadButton.style.display = "block";

            // Scroll to the result section
            resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
        } else {
            console.error('File download failed');
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
}

function browseFiles() {
    document.getElementById("fileInput").click();
}

document.getElementById("selectFolderLink").addEventListener("click", function(event) {
    event.preventDefault();
    document.getElementById("selectFolderSection").style.display = "block";
    document.getElementById("resultSection").style.display = "none";
    document.getElementById("downloadLink").style.display = "none";
});

document.getElementById("convertForm").addEventListener("submit", function(event) {
    event.preventDefault();
    uploadFileAndConvert(); // Call the function to upload file and convert
});

document.getElementById("downloadButton").addEventListener("click", function() {
    const excelFile = document.getElementById("resultSection").querySelector("#excelFile").textContent.split(":")[1].trim();
    window.location.href = `http://localhost:8000/static/${excelFile}`;
});

