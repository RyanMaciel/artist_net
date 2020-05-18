let data = JSON.parse(dataString);

// Updated the info box when a node is clicked.
function handleSelection(selectedData){
    document.getElementById("header").textContent=selectedData;
}

function processJSON(data) {
    // Construct this object which will be of form:
    // {'MovementName': ['artist1', 'artist2', ...], ...}
    let extractedMovements = {};
    let artistNodes = []
    let movementNodes = []
    let links = []
    for(const artistName in data) {
        if(data[artistName] && data[artistName].Movement){
            movements = data[artistName].Movement;
            artistNodes.push({id: artistName});
            movements.forEach((movement)=>{
                links.push({source: artistName, target: movement})
                if(extractedMovements[movement]){
                    extractedMovements[movement].push(artistName);
                } else{
                    extractedMovements[movement] = [artistName];
                    movementNodes.push({id:movement});
                }
            });
        }
    }
    console.log(artistNodes)
    console.log(links)

    let totalNodes = artistNodes.concat(movementNodes)
    return {totalNodes, links}
}

const {totalNodes, links} = processJSON(data);


const width = window.innerWidth
const height = window.innerHeight

const svg = d3.select("body")
    .append("svg")
    .attr("width", width)
    .attr("height", height)

svg.append("rect")
    .attr("width", width)
    .attr("height", height)
    .attr("fill", "white")
    .call(d3.zoom().on("zoom", function () {
        svgContainter.attr("transform", d3.event.transform)
    }));
const svgContainter = svg.append("g");


    


// Set up simulation
const simulation = d3.forceSimulation(totalNodes)
    .force("link", d3.forceLink(links).id(d => d.id)) // this mutates links...IMPLICIT!
    .force('charge', d3.forceManyBody().strength(-20)) 
    .force('center', d3.forceCenter(width / 2, height / 2))

// Set up links
const link = svgContainter.append("g")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
    .selectAll("line")
    .data(links)
    .join("line")
        .attr("stroke-width", 1);

// Set up nodes
const node = svgContainter.append("g")
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
    .selectAll("g")
    .data(totalNodes)
    .join("g") // g here because we want a label/flexible display, not just a circle.
        .attr("class", "node")
        .attr("transform", "translate(" + d3.randomInt(width), + "," + d3.randomInt(height) + ")")
        .on("click", (datum)=>{
            console.log(datum.id)
            handleSelection(datum.id)
        });

node.append("circle")
    .attr("r", 5)
    .attr("fill", 'red')

node.append("title")
    .text(d => d.id);

node.append("text")
    .attr("class", "label")
    .attr("x", 12)
    .attr("dy", ".35em")
    .text(d => d.id);    

simulation.on("tick", () => {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node
        .attr("transform", d => "translate(" + d.x + "," + d.y + ")");
});

invalidation.then(() => simulation.stop());




svg.node();
