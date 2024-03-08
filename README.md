# Dairy Flat Airways
## Assignment submitted for 159.352, Massey University

This was a project completed in 2023 for Massey University's Advanced Web Paper (159.352). The paper covers how web servers work, and the concepts behind APIs and frameworks to create dynamic programs.</p>

**Dairy Flat Airways** is a fictional airline - based out of the (real) North Shore Aerodrome in Auckland, which is near Massey's albany campus. Several regional airlines have operated out of this airport (which has no control tower), and fly to similar destinations to the fictional airline.

The brief was to create a ticketing website where users could find flights, and buy tickets for the scheduled flights.

Most written material is generated from ChatGPT, and images are generated using Dall-E. They are supposed to be horrendous! This was not required for the assignment, but where is the fun in bare bones!</p>

### Features

- All schedule plans are configurations in the database rather than hardcoded - airports, aircraft, scheduled plans etc can be altered and the simulation reseeded</li>
- The plans are converted into scheduled flights as part of the simulation to ensure the demonstration always works</li>
- The flight board is as per simulation</li>
- The flight tracker tracks the simulated flights and plane positions based on server time</li>
- A graph traversing model is used to (a version of Dijkstra's algorithm) find all possible itineraries of scheduled flights between an origin and destination that could be purchased for the travelling group</li>
- User can simulate purchasing tickets
- Carousel to navigate through the information blocks

### Technologies

- <a href="https://www.djangoproject.com/">Django</a>
- HTML/CSS/JS
- <a href="https://www.docker.com/">Docker</a> - to build project in a container
- <a href="https://turfjs.org/">Turf.js</a> - Geospatial Analysis Package. Used to draw points and in particular, geodesic lines to represent what a straight line looks like on the projection
