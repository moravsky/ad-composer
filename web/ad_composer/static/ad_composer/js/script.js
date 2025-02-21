let frame = null;

async function loadUrl() {
    const url = document.getElementById('urlInput').value;
    try {
        const response = await fetch(`/fetch-url/?url=${encodeURIComponent(url)}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const content = await response.text();
        const contentContainer = document.createElement('div');
        contentContainer.innerHTML = content;

        const mainContent = contentContainer.querySelector('main') ||
            contentContainer.querySelector('.body-container') ||
            contentContainer.querySelector('body');

        const rightColumn = document.querySelector('.right-column');
        rightColumn.innerHTML = '';

        if (mainContent) {
            rightColumn.appendChild(mainContent);
        } else {
            rightColumn.innerHTML = content;
        }

        frame = {
            document: {
                body: rightColumn
            }
        };

        enableSelectionMode();

        document.getElementById('selectionInstruction').style.display = 'block';
        document.getElementById('selectedElements').style.display = 'block';

        loadExternalResources(contentContainer);

    } catch (error) {
        console.error('Error loading URL:', error);
        alert(`Failed to load URL: ${error.message}`);
        frame = null;
    }
}

function enableSelectionMode() {
    try {
        if (frame && frame.document && frame.document.body) {
            frame.document.body.addEventListener('mouseover', handleMouseOver);
            frame.document.body.addEventListener('mouseout', handleMouseOut);
            frame.document.body.addEventListener('click', handleClick);
        }
    } catch (error) {
        console.error('Error enabling selection mode:', error);
        alert('Unable to interact with the loaded page.');
    }
}

function disableSelectionMode() {
    try {
        if (frame && frame.document && frame.document.body) {
            frame.document.body.removeEventListener('mouseover', handleMouseOver);
            frame.document.body.removeEventListener('mouseout', handleMouseOut);
            frame.document.body.removeEventListener('click', handleClick);
        }
        
        document.getElementById('selectionInstruction').style.display = 'none';
        document.getElementById('selectedElements').style.display = 'none';
        document.getElementById('elementsList').innerHTML = '';
    } catch (error) {
        console.error('Error disabling selection mode:', error);
    }
}

function handleMouseOver(e) {
    e.stopPropagation();
    e.target.classList.add('hover-highlight');
}

function handleMouseOut(e) {
    e.stopPropagation();
    e.target.classList.remove('hover-highlight');
}

function handleClick(e) {
    e.preventDefault();
    e.stopPropagation();

    const element = e.target;
    element.classList.toggle('selected-element');
    updateSelectedElementsList(element);
}

function updateSelectedElementsList(element) {
    const elementsList = document.getElementById('elementsList');
    const elementId = `sel-${Date.now()}`;
    element.dataset.selectionId = elementId;

    const div = document.createElement('div');
    div.classList.add('selected-item');
    div.innerHTML = `
        <div data-selection-id="${elementId}">
            ${element.tagName.toLowerCase()}: ${element.textContent.slice(0, 50)}...
            <span class="remove-icon" onclick="removeSelectedListItem('${elementId}')">✕</span>
        </div>
    `;
    elementsList.appendChild(div);
}

function removeSelectedListItem(elementId) {
    const selectedItem = document.querySelector(`.selected-item [data-selection-id="${elementId}"]`)
        ? document.querySelector(`.selected-item [data-selection-id="${elementId}"]`).closest('.selected-item')
        : document.querySelector(`.selected-item:has([data-selection-id="${elementId}"])`);

    if (selectedItem) {
        selectedItem.remove();
    }

    const rightColumn = document.querySelector('.right-column');
    if (rightColumn) {
        const originalElement = rightColumn.querySelector(`[data-selection-id="${elementId}"]`);
        if (originalElement) {
            originalElement.classList.remove('selected-element');
            originalElement.removeAttribute('data-selection-id');
        }
    }
}

function loadExternalResources(containerElement) {
    const stylesheets = containerElement.querySelectorAll('link[rel="stylesheet"]');
    stylesheets.forEach(link => {
        const newLink = document.createElement('link');
        newLink.rel = 'stylesheet';
        newLink.href = link.href;
        document.head.appendChild(newLink);
    });

    const scripts = containerElement.querySelectorAll('script[src]');
    scripts.forEach(script => {
        const newScript = document.createElement('script');
        newScript.src = script.src;
        document.head.appendChild(newScript);
    });
}

async function fetchTargets() {
    try {
        const response = await fetch('http://localhost:8080/api/account-names');
        const targets = await response.json();
        const targetsDropdown = document.getElementById('targetsDropdown');

        while (targetsDropdown.options.length > 1) {
            targetsDropdown.remove(1);
        }

        targets.forEach(targetName => {
            const option = document.createElement('option');
            option.value = targetName;
            option.textContent = targetName;
            targetsDropdown.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching targets:', error);
    }
}

function customizeSelectedTarget() {
    const targetsDropdown = document.getElementById('targetsDropdown');
    const selectedTargetId = targetsDropdown.value;
    const selectedElements = document.querySelectorAll('.selected-element');

    if (!selectedTargetId) {
        alert('Please select a target first');
        return;
    }

    if (selectedElements.length === 0) {
        alert('Please select elements to personalize');
        return;
    }

    const selectedTexts = Array.from(selectedElements).map(el => el.textContent.trim());

    const payload = {
        client: selectedTargetId,  // kept as 'client' to match API expectation
        texts: selectedTexts
    };

    fetch('http://localhost:8080/api/personalize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        selectedElements.forEach((element, index) => {
            if (data.personalizedContent && data.personalizedContent[index]) {
                element.textContent = data.personalizedContent[index];
            }
        });

        disableSelectionMode();
        alert('Content personalized successfully! Selection mode is now disabled.');
    })
    .catch(error => {
        console.error('Personalization error:', error);
        alert('Failed to personalize content');
    });
}

// Initialize the application
fetchTargets();