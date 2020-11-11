document.addEventListener('DOMContentLoaded', function() {
    // table of content links work fine, but external links are broken
    // we do some magic here to make external links work

    let sectionMap = [];
    let references = document.getElementsByClassName('reference internal');
    let externalReferences = document.getElementsByClassName('reference external');

    for(let i = 0; i < references.length; i++){
       const element = references[i];
       sectionMap.push({href:element.href, text:element.innerText.toLowerCase()})
    }

    console.log(sectionMap);

    for(let i = 0; i < externalReferences.length; i++){
        let innerText = externalReferences[i].innerText.toLowerCase()
        console.log(innerText);
        let internalReference = sectionMap.find(section=>section.text == innerText);
        if(internalReference){
            console.log("in")
            externalReferences[i].href = internalReference.href;
        }
    }
}, false);