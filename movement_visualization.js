let data = JSON.parse(dataString);

// Construct this object which will be of form:
// {'MovementName': ['artist1', 'artist2', ...], ...}
extractedMovements = {};
artistNodes = []
for(const artistName in data) {
    if(data[artistName] && data[artistName].Movement){
        artistNodes.push({name: artistName});
        movements = data[artistName].Movement;
        movements.forEach((movement)=>{
            if(extractedMovements[movement]){
                extractedMovements[movement].push(artistName)
            } else{
                extractedMovements[movement] = [artistName]
            }
        });
    }
}
console.log(extractedMovements)


const width = window.innerWidth
const height = window.innerHeight

const svg = d3.select("body")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

const node = svg.append("g")
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
    .selectAll("circle")
    .data(artistNodes)
        .join("circle")
        .attr("r", 5)
        .attr("cx", d3.randomInt(width))
        .attr("cy", d3.randomInt(height))
        .attr("fill", 'red');

node.append("title")
    .text(d => d.name);
svg.node();

const simulation = d3.forceSimulation()
  .force('charge', d3.forceManyBody().strength(-20)) 
  .force('center', d3.forceCenter(width / 2, height / 2))
