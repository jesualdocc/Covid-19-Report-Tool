import { Component, OnDestroy, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import * as THREE from 'three';
//import { OrbitControls } from 'three-orbit-controls';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { IGlobeData } from './IGlobeData';
import { ReturnStatement } from '@angular/compiler';
import { Router } from '@angular/router';
//import {COLORS} from './Colors';

const COLORS = ['red', 'yellow', 'blue', 'green', 'purple', 'black', 'magenta', 'orange', 'gold', 'brown', 'lightgreen']

@Component({
  selector: 'app-globe-threejs',
  templateUrl: './globe-threejs.component.html',
  styleUrls: ['./globe-threejs.component.css'],
})
export class GlobeThreejsComponent implements OnInit, OnDestroy {
  private data: IGlobeData[] = []; //holds api data
  scene: THREE.Scene; //where objects will be placed (kind of like a stage)
  camera: THREE.PerspectiveCamera = new THREE.PerspectiveCamera(75,window.innerWidth / window.innerHeight,0.1,1000);
  renderer: THREE.WebGLRenderer; //display the created objects
  raycaster: THREE.Raycaster; //raycaster for mouse interaction
  mouse: THREE.Vector2; // CREATE vector2 for mouse x,y coordinates
  lManager:THREE.LoadingManager = new THREE.LoadingManager();

  earthClouds: THREE.Mesh;
  controls: OrbitControls;
  loadingData: boolean = false;
  changingLocationLoading = false;
  disableshowLocationsButton:boolean = false;

  pointData:IGlobeData;

  get myPointData():IGlobeData{
    //Shouldnt become undefined, but it prevents the app from freezing if it does
    if(this.pointData == undefined){
      this.pointData = {country:'*', state:'*', county:'*', cases:0, deaths:0, population:0, latitude:0, longitude:0};
      return this.pointData;
    }
    else{
      return this.pointData;
    }

  }
  countries:Set<string> = new Set()
  states:string[] = ['All'];
  counties:string[] = ['All'];
  selectedCountry:string;
  selected_Province_State:string;
  selectedCounty:string;
  changePointRadiusSize = false;

  get showProvincesState():boolean{
    return this.states.length > 1;
  }

  get showCounties():boolean{
    return this.counties.length > 1;
  }

  //Change buttons name depending on values
  showInstructionsBox: boolean = true;
  get buttonNameInst(): string {

    return this.showInstructionsBox ? 'Hide Instructions' : 'Show Instructions';
  }

  private animationId: number;
  title = 'Globe';

  constructor(private dataService: DataService, private router:Router) {
    this.dataService.changePageTitle(this.title);
    this.dataService.changeView(true);
    this.run();
  }

  ngOnDestroy(): void {
    //Stop animation and delete all objects
    cancelAnimationFrame(this.animationId);

    document.body.removeChild(this.renderer.domElement);
    this.scene.clear();
    this.renderer.dispose();
    this.camera.clear();
    this.controls.dispose();
  }

  ngOnInit(): void {}

  async run() {
    await this.getData();
    this.createScene();
    this.setupCamera();
    this.setupMouseInteractivity();
    this.configureRenderer();
    this.createEarth();
    this.addListeners();
    this.setupControls();

    this.animate();
  }

  // Allows for the scene to move and be interacted with
  animate() {
    this.animationId = requestAnimationFrame(this.animate.bind(this));
    this.renderer.render(this.scene, this.camera);
    this.controls.update();
  }

  private createScene() {
    //where objects will be placed (kind of like a stage)
    this.scene = new THREE.Scene();
  }

  setupCamera() {
    // Change position so we can see the objects (change x, y for default country/continent view)
    this.camera.position.x = -3.5;
    this.camera.position.y = 13.5;
    this.camera.position.z = 10;
    //Returns camera to default settings
  }

  private setupControls() {
    // CREATE controls so that we can interact with the objects/have interactivity
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);

    // Disable control function, so users do not zoom too far in or pan away from center
    this.controls.minDistance = 12;
    this.controls.maxDistance = 30;
    this.controls.enablePan = false;
    this.controls.update();
    this.controls.saveState();
  }

  private setupMouseInteractivity() {
    this.raycaster = new THREE.Raycaster(); //raycaster for mouse interaction
    this.mouse = new THREE.Vector2(); // CREATE vector2 for mouse x,y coordinates
  }

  private createEarth() {
    // Earthmap is used for the basic texture which has the various continents/countries/etc. on it
    let earthMap = new THREE.TextureLoader().load(
      'assets/myglobe_images/earthmap4k.jpg'
    );

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

    this.createCloudTextures(); //Add clouds to earth
    earth.add(this.earthClouds);

    //Add earth to the scene
    this.scene.add(earth);

    this.createSkyBox();
    this.createLights();

  }

  private createCloudTextures() {
    return new Promise((resolve, reject) => {
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
    this.earthClouds = new THREE.Mesh(earthCloudGeo, earthMaterialClouds);

    // Scale above the earth sphere mesh
    this.earthClouds.scale.set(1.015, 1.015, 1.015);

    resolve(true);
  });
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
  private addCountyCoord(
    country,
    state,
    county,
    cases,
    deaths,
    latitude,
    longitude,
    population,
    color
  ) {

    //0.035 for counties only
    let sphereRadiusSize:number = this.changePointRadiusSize ? 0.035:0.1;
    let pointOfInterest = new THREE.SphereGeometry(sphereRadiusSize, 32, 32);
    let lat = latitude * (Math.PI / 180);
    let lon = -longitude * (Math.PI / 180);
    const radius = 10;


    let material = new THREE.MeshBasicMaterial({
      color: color,
    });

    let mesh = new THREE.Mesh(pointOfInterest, material);

    mesh.position.set(
      Math.cos(lat) * Math.cos(lon) * radius,
      Math.sin(lat) * radius,
      Math.cos(lat) * Math.sin(lon) * radius
    );

    mesh.rotation.set(0.0, -lon, lat - Math.PI * 0.5);

    mesh.userData.country = country;
    mesh.userData.state = state;
    mesh.userData.county = county;
    mesh.userData.population = population;
    mesh.userData.color = color;
    mesh.userData.cases = cases;
    mesh.userData.deaths = deaths;

    this.earthClouds.add(mesh);
  }

  // Changes the information so data points can be seen
  addLocationData(type:string) {
          this.changingLocationLoading = true;
          var filteredData:IGlobeData[] = this.data.filter(data=> data.country == this.selectedCountry);
          this.changePointRadiusSize = false;
          this.removeChildren();

          if(type == 'Country'){

              this.counties = ['All'];
              this.states = ['All'];
              if(this.selectedCountry == 'US'){

                //Filter further to avoid slowing dow browser since there is a lot of data for the US
                this.updateDisplayBoard(filteredData, type);

                //Include one county per state for mapping points on globe - representing state points
                var tmp:IGlobeData[] = [];
                let statesAdded:string[] = [];
                for(let i = 0; i < filteredData.length; i++){

                  if(!statesAdded.includes(filteredData[i].state)){
                    statesAdded.push(filteredData[i].state);
                    tmp.push(filteredData[i]);
                  }
                }
                let tmpArr = ['All'].concat(statesAdded.sort());
                this.states =  tmpArr;
                filteredData = tmp;

              }
              else{

                this.updateDisplayBoard(filteredData, type);

                if(this.selectedCountry == 'World'){
                  //Show all countries points
                  filteredData = this.data.filter(data=> data.state == null || data.state == '*');

                }
                else{

                  for(let i = 0; i < filteredData.length; i++){
                    if(filteredData[i].state != null){
                      this.states.push(filteredData[i].state)
                    }
                  }
                }
              }
              this.selected_Province_State == null;
          }

        else if(type == 'Prov_State'){
            this.selectedCounty = null;
            this.counties = ['All'];

              if(this.selected_Province_State != 'All' && this.selected_Province_State != null){
                filteredData = this.data.filter(data=> data.state == this.selected_Province_State);
                this.updateDisplayBoard(filteredData, type);

                if(this.selectedCountry == 'US'){
                  this.updateTotals(filteredData);
                  this.changePointRadiusSize = true;
                }
              }
              else{
                this.changePointRadiusSize = false;
                this.updateDisplayBoard(filteredData, type);
              }
        }
        else{
           //County Data

          if(this.selected_Province_State != 'All' && this.selected_Province_State != null){

            filteredData = this.data.filter(data=> data.state == this.selected_Province_State);
          }

              if(this.selectedCounty != 'All' && this.selectedCounty != null){
                this.changePointRadiusSize = false;
                filteredData = filteredData.filter(data=> data.county == this.selectedCounty);
                this.updateDisplayBoard(filteredData, type);

              }

              else{

                this.counties = ['All'];
                this.changePointRadiusSize = true;
                this.updateTotals(filteredData);
              }
          }
        this.removeBlanksandSymbols();
        //console.log(filteredData)
      // Insert data  into the globe (points)
        let numOfColors = COLORS.length;
        for (let i = 0, colorIndex = 0; i < filteredData.length; i++, colorIndex++) {

          if(colorIndex == numOfColors){
            colorIndex = 0; //Repeat colors if list of colors if less than data points
          }
          //COLOR[colorIndex] - gives different colors to each point
          this.addCountyCoord(filteredData[i].country, filteredData[i].state, filteredData[i].county, filteredData[i].cases, filteredData[i].deaths, filteredData[i].latitude, filteredData[i].longitude, filteredData[i].population, COLORS[colorIndex]);

        }

        this.changingLocationLoading = false;
  }

  //Updated display info without click on globe
  private updateDisplayBoard(filteredData:IGlobeData[], type:string){
    if(type == 'Country'){
      filteredData = filteredData.filter(data=> data.state == null || data.state == '*');
      this.pointData = filteredData[0];
      this.pointData.state = '*';
      this.pointData.county = '*';
    }
    else if(type == 'Prov_State'){
      this.pointData = filteredData[0];
      this.pointData.county = '*';
    }
    else{
      this.pointData = filteredData[0];
    }

  }

  private removeBlanksandSymbols(){
    let index = this.states.indexOf('*');
    if (index > -1) {
      this.states.splice(index, 1);
    }

    index = this.states.indexOf('');
    if (index > -1) {
      this.states.splice(index, 1);
    }

    index = this.states.indexOf(' ');
    if (index > -1) {
      this.states.splice(index, 1);
    }

    index = this.counties.indexOf('*');
    if (index > -1) {
      this.counties.splice(index, 1);
    }

    index = this.counties.indexOf('');
    if (index > -1) {
      this.counties.splice(index, 1);
    }

    index = this.counties.indexOf(' ');
    if (index > -1) {
      this.counties.splice(index, 1);
    }

  }

  //Updates totals by state to be displayed when a state is chosen
  private updateTotals(filteredData:IGlobeData[]){
              let totalCases = 0;
              let totalDeaths = 0;
              let totalPopulation = 0;

              for(let i = 0; i < filteredData.length; i++){
                this.counties.push(filteredData[i].county)
                totalCases += filteredData[i].cases;
                totalDeaths += filteredData[i].deaths;
                totalPopulation += filteredData[i].population;
              }
              //State/Province data
              this.pointData.country = this.selectedCountry;
              this.pointData.state = this.selected_Province_State;
              this.pointData.cases = totalCases;
              this.pointData.deaths = totalDeaths;
              this.pointData.population = totalPopulation;
              this.pointData.county = '*';

  }

  // Removes the points of interest freeing up memory and space to have better performance
  private removeChildren() {
    let destroy = this.earthClouds.children.length;
    while (destroy--) {
      //this.earthClouds.remove(this.earthClouds.children[destroy].material.dispose())
      //this.earthClouds.remove(this.earthClouds.children[destroy].geometry.dispose())
      this.earthClouds.remove(this.earthClouds.children[destroy]);
    }
  }

  // Add event listeners so DOM knows what functions to use when objects/items are interacted with
  addListeners() {
    window.addEventListener('resize', this.onWindowResize.bind(this), false);
    window.addEventListener('click', this.onWindowClick.bind(this), false);
  }

  // Resizes the window when it changes
  private onWindowResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  // Listens for the mouse to intersect object and when clicked returns the data to the inner html
  private onWindowClick(event) {
    event.preventDefault();
    this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    this.raycaster.setFromCamera(this.mouse, this.camera);

    let intersects = this.raycaster.intersectObjects(this.earthClouds.children);
    if(intersects[0] != undefined){

      var tmpData:any = intersects[0].object.userData;
      this.pointData = tmpData;
      let point = intersects[0].point;
      this.camera.position.copy(point).normalize(); //move camera a bit closer to point selected

    }

  }

  //Toggles instruction box
  displayInstructionsBox() {
    this.showInstructionsBox = !this.showInstructionsBox;
  }
exit(){

  this.router.navigate(['home']).then(()=>{
    //Reloads application to better display the other pages without being affected by threejs
    window.location.reload();
  });

}
  //Retrieve data from API
  private getData() {
    return new Promise((resolve, reject) => {
      this.loadingData = true;
      this.dataService.getGlobeData().subscribe(
        (result) => {
          if (result.status == 200) {
            this.data = result.body['data'];
          }

          this.countries.add('World');
          this.countries.add('US');
          for(let i = 0; i < this.data.length; i++){
            this.countries.add(this.data[i].country)
          }

        },
        (err) => {
          reject(false)
        },

        () => {
          //Resolve when complete
          this.loadingData = false;
          resolve(true);
        }
      );
    });
  }

}
