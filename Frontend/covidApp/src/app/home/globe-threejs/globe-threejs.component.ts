import { Component, OnInit } from '@angular/core';
import * as THREE from 'three';
import { OrbitControls } from 'three-orbit-controls';
import {IGlobeData} from './IGlobeData';

@Component({
  selector: 'app-globe-threejs',
  templateUrl: './globe-threejs.component.html',
  styleUrls: ['./globe-threejs.component.css'],
})
export class GlobeThreejsComponent implements OnInit {

  data:IGlobeData [] = [];
  public scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  private earthClouds:THREE.Mesh;
  public controls: OrbitControls;

  constructor() {}

  ngOnInit(): void {}

  start(){
    this.createScene()
    this.createEarth()
  }

  private createEarth() {
    // Earthmap is used for the basic texture which has the various continents/countries/etc. on it
    let earthMap = new THREE.TextureLoader().load('./images/earthmap4k.jpg');

    // EarthBumpMap is used to give the texture some "depth" so it is more appealing on eyes and data visuals
    let earthBumpMap = new THREE.TextureLoader().load(
      './images/earthbump4k.jpg'
    );

    // EarthSpecMap gies the earth some shininess to the environment, allowing reflectivity off of the lights
    let earthSpecMap = new THREE.TextureLoader().load(
      '../images/earthspec4k.jpg'
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
      './images/earthhiresclouds4K.jpg'
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
      '../images/space_right.png',
      '../images/space_left.png',
      '../images/space_top.png',
      '../images/space_bot.png',
      '../images/space_front.png',
      '../images/space_back.png',
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

  createCamera() {
    this.camera = new THREE.PerspectiveCamera(75,window.innerWidth / window.innerHeight,0.1,1000);
    // Change position so we can see the objects
    this.camera.position.z = 20;

  }

  private createControls(){
    // CREATE controls so that we can interact with the objects/have interactivity
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);

    // Disable control function, so users do not zoom too far in or pan away from center
    this.controls.minDistance = 12;
    this.controls.maxDistance = 30;
    this.controls.enablePan = false;
    this.controls.update();
    this.controls.saveState();

  }

  private createScene() {
    //scene is where objects will be placed (kind of like a stage)
    this.scene = new THREE.Scene();
  }

  private startRendering() {
    // CREATE renderer to display the created objects (kind of like the people who place the diferent sets on the stage)
    this.renderer = new THREE.WebGLRenderer();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(this.renderer.domElement);
  }

//   // Create and add coordinates for the globe
private addCountyCoord(state, county, cases, deaths, latitude, longitude, color){
  let pointOfInterest = new THREE.SphereGeometry(.1, 32, 32);
  let lat = latitude * (Math.PI/180);
  let lon = -longitude * (Math.PI/180);
  const radius = 10;
  const phi = (90-lat)*(Math.PI/180);
  const theta = (lon+180)*(Math.PI/180);

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
      this.addCountyCoord(this.data[i].state, this.data[i].county, this.data[i].cases, this.data[i].deaths, this.data[i].latitude, this.data[i].longitude, 'red');
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

}
