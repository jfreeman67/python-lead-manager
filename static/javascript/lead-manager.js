let currentPage = 1;
let totalPageCnt = 1;
let totalRecords = 1;
let leadStatusMap = {}; // hash for lead statuses
let currentRecordId = null;

// Create a debounced version of searchRecords with a delay
const debouncedSearchRecords = debounce(searchRecords, 300);  // 300 ms delay

document.addEventListener("DOMContentLoaded", () => {
    loadLeadStatuses(); // Load lead statuses when the page is loaded
    getRecords(); // load first 10 records
});

// Use the debounced function in the event listener
document.getElementById("search-input").addEventListener("input", debouncedSearchRecords);

// Function to open the edit modal and populate it with record data
function editRecord(id, name, email, phone, status, lastUpdated) {
    currentRecordId = id;
    document.getElementById('edit-name').value = name;
    document.getElementById('edit-email').value = email;
    document.getElementById('edit-phone').value = phone;
    document.getElementById('last-updated').textContent = `Last Updated: ${lastUpdated}`;

    // Set the status dropdown based on the current status
    const statusDropdown = document.getElementById('edit-status');
    statusDropdown.innerHTML = "";

    // Populate dropdown from leadStatusMap
    for (const [key, value] of Object.entries(leadStatusMap)) {
        const option = document.createElement("option");
        option.value = key;
        option.textContent = value;
        if (key === status) {
            option.selected = true;
        }
        statusDropdown.appendChild(option);
    }

    // Show the modal
    document.getElementById('edit-modal').style.display = 'block';
}

// Close the edit modal
function closeEditModal() {
    document.getElementById('edit-modal').style.display = 'none';
}

// Function to save changes
function saveChanges(event) {
    event.preventDefault();

    const name = document.getElementById('edit-name').value;
    const email = document.getElementById('edit-email').value;
    const phone = document.getElementById('edit-phone').value;
    const status = document.getElementById('edit-status').value;

    // Send a request to update the record on the server
    fetch(`/update_lead/${currentRecordId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, email, phone, status })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.message) {
            alert(data.message);
            getRecords();
        } else if (data.error) {
            alert(data.error);
        }
    })
    .catch(error => {
        console.error("Fetch error:", error);
        alert('An error occurred while trying to update the record.');
    });

    closeEditModal();
}

// Load lead statuses for the dropdown
function loadLeadStatusesForEdit() {
    fetch('/lead_statuses')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === '200') {
                populateEditStatusDropdown(data.lead_statuses);
            } else {
                console.error("Error:", data.message);
            }
        })
        .catch(error => {
            console.error("Fetch error:", error);
        });
}

function populateEditStatusDropdown(leadStatuses) {
    const statusDropdown = document.getElementById("edit-status");
    statusDropdown.innerHTML = "";

    leadStatuses.forEach(status => {
        const option = document.createElement("option");
        option.value = status.id;
        option.textContent = status.name;
        statusDropdown.appendChild(option);
    });
}

// Delete record with confirmation
function deleteRecord(id) {
    if (confirm("Are you sure you want to delete this record?")) {
        fetch(`/delete_lead/${id}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.message) {
                alert(data.message);
                getRecords();
            } else if (data.error) {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error("Fetch error:", error);
            alert('An error occurred while trying to delete the record.');
        });
    }
}

function searchRecords() {
    currentPage = 1;
    getRecords();
}

function getRecords() {
    const searchQuery = document.getElementById("search-input").value.trim();
    const selectedStatus = document.getElementById("status-filter").value;

    // console.log('searchRecords : searchQuery='+searchQuery+' selectedStatus='+selectedStatus);

    fetch(`/searches?search=${encodeURIComponent(searchQuery)}&page=${currentPage}&statusFilter=${selectedStatus}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === '200') {
                displayRecords(data.leads_list, data.totalrecords, data.page, data.totalpages);
            } else {
                console.error("Error:", data.message);
            }
        })
        .catch(error => {
            console.error("Fetch error:", error);
        });
}

function debounce(func, delay) {
    let debounceTimer;
    return function (...args) {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => func.apply(this, args), delay);
    };
  }
  
function displayRecords(leads, totalRecords, currentPage, totalPages) {
    const recordsBody = document.querySelector("#records tbody");
    recordsBody.innerHTML = "";
    totalPageCnt = totalPages;

    leads.forEach(lead => {
        const leadStatusDesc = leadStatusMap[lead.lead_status_id] || "Unknown";
        const row = document.createElement("tr");
        
        // Create HTML structure for each field, including links for actions
        row.innerHTML = `
            <td>${lead.name}</td>
            <td>${lead.email}</td>
            <td>${lead.phone}</td>
            <td>${leadStatusDesc}</td>
            <td class="actions">
                <a href="#" onclick="editRecord('${lead.id}', '${lead.name}', '${lead.email}', '${lead.phone}', '${lead.lead_status_id}', '${lead.updated_at}')" class="link-button">Edit</a>
                <a href="#" onclick="deleteRecord('${lead.id}')" class="link-button">Delete</a>
            </td>
        `;
        
        recordsBody.appendChild(row);
    });

    // Update total records and pagination information
    document.getElementById("total-records").textContent = `Total Records: ${totalRecords}`;
    document.getElementById("current-page").textContent = `Page ${currentPage} of ${totalPages}`;
}

// Pagination logic
function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        updatePageInfo();
        loadPage(currentPage);
    }
}

function nextPage() {
    if (totalPageCnt > currentPage) {
        currentPage++;
        updatePageInfo();
        loadPage(currentPage);
    }
}

function updatePageInfo() {
    document.getElementById('current-page').innerText = `Page ${currentPage}`;
}

function loadPage(page) {
    console.log(`Loading page ${page}`);
    getRecords();
}

function loadLeadStatuses() {
    fetch('/lead_statuses')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === '200') {
                populateLeadStatuses(data.lead_statuses);
                createLeadStatusMap(data.lead_statuses);
            } else {
                console.error("Error:", data.message);
            }
        })
        .catch(error => {
            console.error("Fetch error:", error);
        });
}

function populateLeadStatuses(leadStatuses) {
    const statusFilter = document.getElementById("status-filter");
    statusFilter.innerHTML = "";

    // Add a default option for "All"
    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "All Statuses";
    statusFilter.appendChild(defaultOption);

    // Populate dropdown with lead statuses
    leadStatuses.forEach(status => {
        const option = document.createElement("option");
        option.value = status.id;
        option.textContent = status.name;
        statusFilter.appendChild(option);
    });
}

function createLeadStatusMap(leadStatuses) {
    leadStatuses.forEach(status => {
        leadStatusMap[status.id] = status.name; // Store each status name by its ID
    });
}

function openCreateLeadModal() {
    // Gather data from the form
    const name = document.getElementById('new-name').value;
    const email = document.getElementById('new-email').value;
    const phone = document.getElementById('new-phone').value;
    const status = document.getElementById('new-status').value;

    // Set the status dropdown based on the current status
    const statusDropdown = document.getElementById('new-status');
    statusDropdown.innerHTML = ""; // Clear existing options

    // Populate dropdown from leadStatusMap
    for (const [key, value] of Object.entries(leadStatusMap)) {
        const option = document.createElement("option");
        option.value = key;
        option.textContent = value;
        if (key === status) {
            option.selected = true;
        }
        statusDropdown.appendChild(option);
    }

    document.getElementById('create-modal').style.display = 'block';
}

function closeCreateModal() {
    document.getElementById('create-modal').style.display = 'none';
}

function createLead(event) {
    event.preventDefault(); // Prevent the default form submission

    // Gather data from the form
    const name = document.getElementById('new-name').value;
    const email = document.getElementById('new-email').value;
    const phone = document.getElementById('new-phone').value;
    const status = document.getElementById('new-status').value;

    // Validate form fields (basic validation example)
    if (!name || !email || !phone || !status) {
        alert("Please fill in all fields.");
        return;
    }

    // Prepare the data to send in the request
    const leadData = {
        name: name,
        email: email,
        phone: phone,
        status: status
    };

    // Send a POST request to create a new lead
    fetch('/create_lead', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(leadData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to create lead');
        }
        return response.json();
    })
    .then(data => {
        alert('Lead created successfully');
        closeCreateLeadModal();
        getRecords();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('There was an error creating the lead. Please try again.');
    });
}

function closeCreateLeadModal() {
    const modal = document.getElementById('create-modal');
    if (modal) {
        modal.style.display = 'none';
    } else {
        console.warn("Modal with ID 'create-modal' not found.");
    }
}
