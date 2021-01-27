import { Component, OnDestroy, OnInit } from '@angular/core';
import { animationFrameScheduler } from 'rxjs';
import { DataService } from 'src/app/services/data.service';
import * as THREE from 'three';
//import { OrbitControls } from 'three-orbit-controls';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import {IGlobeData} from './IGlobeData';

@Component({
  selector: 'app-globe-threejs',
  templateUrl: './globe-threejs.component.html',
  styleUrls: ['./globe-threejs.component.css'],
})
export class GlobeThreejsComponent implements OnInit, OnDestroy {

  private data:IGlobeData [] = []; //holds api data
  scene:THREE.Scene; //where objects will be placed (kind of like a stage)
  camera:THREE.PerspectiveCamera = new THREE.PerspectiveCamera(75,window.innerWidth / window.innerHeight,0.1,1000);
  renderer:THREE.WebGLRenderer; //display the created objects
  raycaster:THREE.Raycaster; //raycaster for mouse interaction
  mouse:THREE.Vector2; // CREATE vector2 for mouse x,y coordinates

  earthClouds:THREE.Mesh;
  controls: OrbitControls;

  loadindData:boolean = false;
  showInstructionsBox:boolean = true;
  //Change button name depending value of showInstructionsBox
  get buttonNameInst():string{
    return this.showInstructionsBox ? 'Hide Instructions':'Show Instructions';
  }

  private animationId:number;

  constructor(private dataService:DataService) {
    this.dataService.changeView(true);
    this.start();

  }
  ngOnDestroy(): void {
    //Stop animation and delete all objects
    cancelAnimationFrame(this.animationId);

    document.body.removeChild(this.renderer.domElement);
    this.scene.clear()
    this.renderer.dispose()
    this.camera.clear();
    this.controls.dispose();

  }

  ngOnInit(): void { }

  start(){
    this.getData();
    this.createScene()
    this.setupCamera();
    this.setupMouseInteractivity();
    this.configureRenderer();
    this.addListeners()
    this.createEarth();
    this.setupControls();

    this.animate()
  }

  // Allows for the scene to move and be interacted with
  animate(){
    this.animationId = requestAnimationFrame(this.animate.bind(this));
    this.renderer.render(this.scene, this.camera);
    this.controls.update();
  }

  private createScene(){
    //where objects will be placed (kind of like a stage)
    this.scene = new THREE.Scene();
  }

  setupCamera() {

    // Change position so we can see the objects (change x, y for default country/continent view)
    this.camera.position.x = -3.5;
    this.camera.position.y = 13.5;
    this.camera.position.z = 15;
    //Returns camera to default settings
  }


  private setupControls(){
    // CREATE controls so that we can interact with the objects/have interactivity
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);

    // Disable control function, so users do not zoom too far in or pan away from center
    this.controls.minDistance = 12;
    this.controls.maxDistance = 30;
    this.controls.enablePan = false;
    this.controls.update();
    this.controls.saveState();

  }

  private setupMouseInteractivity(){
    this.raycaster = new THREE.Raycaster(); //raycaster for mouse interaction
    this.mouse = new THREE.Vector2(); // CREATE vector2 for mouse x,y coordinates
  }


  private createEarth() {
    // Earthmap is used for the basic texture which has the various continents/countries/etc. on it
    let earthMap = new THREE.TextureLoader().load('assets/myglobe_images/earthmap4k.jpg');

    // EarthBumpMap is used to give the texture some "depth" so it is more appealing on eyes and data visuals
    let earthBumpMap = new THREE.TextureLoader().load(
      'assets/myglobe_images/earthbump4k.jpg'
    );

    // EarthSpecMap gies the earth some shininess to the environment, allowing reflectivity off of the lights
    let earthSpecMap = new THREE.TextureLoader().load(
      'assets/myglobe_images/earthspec4k.jpg'
    );

    // Geometry is what the shape/size of the globe will be
    let earthGeometry = new THREE.SphereGeometry(10, 32, 32);

    // Material is how the globe will look like
    let earthMaterial = new THREE.MeshPhongMaterial({
      map: earthMap,
      bumpMap: earthBumpMap,
      bumpScale: 0.1,
      specularMap: earthSpecMap,
      specular: new THREE.Color('grey'),
    });

    // Earth is the final product which ends up being rendered on scene, also is used as a grandparent for the points of interest
    let earth = new THREE.Mesh(earthGeometry, earthMaterial);

    this.earthClouds = this.createCloudTextures()
    earth.add(this.earthClouds); //Add clouds to earth

     //Add earth to the scene
    this.scene.add(earth);

    this.createSkyBox();
    this.createLights();

  }

  private createCloudTextures() {
    // Add clouds to the earth object
    let earthCloudGeo = new THREE.SphereGeometry(10, 32, 32);

    // Add cloud texture
    let earthCloudsTexture = new THREE.TextureLoader().load(
      'assets/myglobe_images/earthhiresclouds4K.jpg'
    );

    // Add cloud material
    let earthMaterialClouds = new THREE.MeshLambertMaterial({
      color: 0xffffff,
      map: earthCloudsTexture,
      transparent: true,
      opacity: 0.4,
    });

    // Create final texture for clouds
    let earthClouds = new THREE.Mesh(earthCloudGeo, earthMaterialClouds);

    // Scale above the earth sphere mesh
    earthClouds.scale.set(1.015, 1.015, 1.015);

    return earthClouds;
  }

  private createSkyBox() {
    //  allows the scene to have more attractiveness to it, in this case by having the blue starred images around Earth

    let loader = new THREE.CubeTextureLoader();
    let texture = loader.load([
      'assets/myglobe_images/space_right.png',
      'assets/myglobe_images/space_left.png',
      'assets/myglobe_images/space_top.png',
      'assets/myglobe_images/space_bot.png',
      'assets/myglobe_images/space_front.png',
      'assets/myglobe_images/space_back.png',
    ]);
    this.scene.background = texture;
  }

  private createLights() {
    let lights = [];
    lights[0] = new THREE.PointLight('#004d99', 0.5, 0);
    lights[1] = new THREE.PointLight('#004d99', 0.5, 0);
    lights[2] = new THREE.PointLight('#004d99', 0.7, 0);
    lights[3] = new THREE.AmbientLight('#ffffff');

    lights[0].position.set(200, 0, -400);
    lights[1].position.set(200, 200, 400);
    lights[2].position.set(-200, -200, -50);

    //creates the lights to be added them to the scene.
    for (let i = 0; i < lights.length; i++) {
      this.scene.add(lights[i]);
    }
  }


  private configureRenderer() {
    this.renderer = new THREE.WebGLRenderer();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(this.renderer.domElement);

  }

//   // Create and add coordinates for the globe
private addCountyCoord(state, county, cases, deaths, latitude, longitude, population, color){
  let pointOfInterest = new THREE.SphereGeometry(0.1, 32, 32);
  let lat = latitude * (Math.PI / 180);
  let lon = -longitude * (Math.PI / 180);
  const radius = 10;
  //const phi = (90 - lat) * (Math.PI / 180);
  //const theta = (lon + 180) * (Math.PI / 180);

  let material = new THREE.MeshBasicMaterial({
      color:color
  });

  let mesh = new THREE.Mesh(
      pointOfInterest,
      material
  );

  mesh.position.set(
      Math.cos(lat) * Math.cos(lon) * radius,
      Math.sin(lat) * radius,
      Math.cos(lat) * Math.sin(lon) * radius
  );

  mesh.rotation.set(0.0, -lon, lat-Math.PI*0.5);

  mesh.userData.state = state;
  mesh.userData.county = county;
  mesh.userData.population = population;
  mesh.userData.color = color;
  mesh.userData.cases = cases;
  mesh.userData.color = deaths;


  this.earthClouds.add(mesh)

};

// Changes the information so data points can be seen
private changeToCounty() {
  // Show/hide needed and unneeded elements
  //document.querySelector("#instruction-box").style.display = "none";
  document.getElementById("title-box").style.display = "none";
  document.getElementById("info-box").style.display = "flex";

  this.removeChildren();

  // Get the data from the JSON file
  for (let i = 0; i < this.data.length; i++){
      this.addCountyCoord(this.data[i].state, this.data[i].county, this.data[i].cases, this.data[i].deaths, this.data[i].latitude, this.data[i].longitude, this.data[i].population ,'red');
  }
};

  // Removes the points of interest freeing up memory and space to have better performance
private removeChildren(){
  let destroy = this.earthClouds.children.length;
  while(destroy--) {
      //this.earthClouds.remove(this.earthClouds.children[destroy].material.dispose())
      //this.earthClouds.remove(this.earthClouds.children[destroy].geometry.dispose())
      this.earthClouds.remove(this.earthClouds.children[destroy])
  }
};

  // Add event listeners so DOM knows what functions to use when objects/items are interacted with
  addListeners(){
    window.addEventListener('resize', this.onWindowResize.bind(this), false);
    window.addEventListener('click', this.onWindowClick.bind(this), false);

  }

  // Resizes the window when it changes
private onWindowResize() {
  this.camera.aspect = window.innerWidth / window.innerHeight;
  this.camera.updateProjectionMatrix();
  this.renderer.setSize(window.innerWidth, window.innerHeight);
};

// Listens for the mouse to intersect object and when clicked returns the data to the inner html
private onWindowClick(event) {
  event.preventDefault();
  this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  this.mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;
  this.raycaster.setFromCamera(this.mouse, this.camera);

  let intersects = this.raycaster.intersectObjects(this.earthClouds.children);

  // for (let i = 0; i < intersects.length; i++){
  //     document.querySelector("#region").innerText = "Region: " + intersects[0].object.userData.region;
  //     document.getElementById("region").style.color = intersects[0].object.userData.color;
  //     document.querySelector("#country-info").innerText = "Country: " + intersects[0].object.userData.country;
  //     document.querySelector("#language").innerText = "Language: " + intersects[0].object.userData.language;
  //     document.querySelector("#population").innerText = "Population: " + intersects[0].object.userData.population;
  //     document.querySelector("#area-sq-mi").innerText = "Area(mile^2): " + intersects[0].object.userData.area_sq_mi;
  //     document.querySelector("#gdp-per-capita").innerText = "GDP Per-Capita: " + intersects[0].object.userData.gdp_per_capita;
  //     document.querySelector("#climate").innerText = "Climate: " + intersects[0].object.userData.climate;
  // }
  // const item = intersects[0];
  // let point = item.point;
  // let camDistance = this.camera.position.copy(point).normalize().multiplyScalar(camDistance);
};

displayInstructionsBox(){
  console.log('clicked')
  this.showInstructionsBox = !this.showInstructionsBox;
}

  //Retrieve data from API
private getData(){
  this.loadindData = true;
  this.dataService.getGlobeData().subscribe(result=>{

    if (result.status == 200){
      var tmp_data =  result.body['data'];
      this.data = tmp_data;

    }

    this.loadindData = false;
  },
    err=>{

      this.loadindData = false;

    });

}

}
