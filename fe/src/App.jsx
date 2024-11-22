import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

function App() {
  const mountRef = useRef(null);
  const intervalRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const objects = useRef({ boxes: [], robots: [], storages: [] });

  const [sliderGridSize, setSliderGridSize] = useState(80);
  const [number, setNumber] = useState(40);
  const [simSpeed, setSimSpeed] = useState(2);
  const [boxes, setBoxes] = useState([]);
  const [robots, setRobots] = useState([]);
  const [storages, setStorages] = useState([]);
  const [location, setLocation] = useState("");
  const [iterations, setIterations] = useState(0);
  const [deliveredPerc, setDeliveredPerc] = useState(0);
  const [running, setRunning] = useState(false);

  // State for managing dynamic boxes
  const [dynamicBoxes, setDynamicBoxes] = useState([]);
  const [newBox, setNewBox] = useState({ name: '', width: '', height: '', depth: '', weight: '' });

  useEffect(() => {
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xffffff);
  
    const gridSize = sliderGridSize * 5;
    const center = gridSize / 2;
  
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1010);
    // Posicionamos la cámara mirando hacia el centro del grid
    camera.position.set(center, sliderGridSize * 2, center * 2);
  
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth / 2, window.innerHeight / 2);
    mountRef.current.appendChild(renderer.domElement);
  
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
  
    // Configuramos el punto de rotación al centro del grid
    controls.target.set(center, 0, center);
  
    const gridHelper = new THREE.GridHelper(gridSize, sliderGridSize);
    gridHelper.position.set(center + 2.5, 0, center + 2.5);
    scene.add(gridHelper);
  
    const ambientLight = new THREE.AmbientLight(0x404040);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(gridSize, gridSize * 2, gridSize);
    scene.add(ambientLight, directionalLight);
  
    sceneRef.current = scene;
    rendererRef.current = renderer;
  
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();
  
    return () => {
      mountRef.current.removeChild(renderer.domElement);
      clearInterval(intervalRef.current);
    };
  }, [sliderGridSize]);  

  const setup = () => {
    fetch("http://localhost:8000/simulations", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dim: [sliderGridSize, sliderGridSize], number }),
    })
      .then((response) => response.json())
      .then((data) => {
        setLocation(data.Location);
        setBoxes(data.boxes);
        setRobots(data.robots);
        setStorages(data.storages);
        setIterations(0);
        setDeliveredPerc(0);
        initializeScene(data);
      });
  };

  const handleStart = () => {
    if (!location || running) return;

    setRunning(true);
    intervalRef.current = setInterval(() => {
      fetch(`http://localhost:8000${location}`)
        .then((response) => response.json())
        .then((data) => {
          setBoxes(data.boxes);
          setRobots(data.robots);
          setStorages(data.storages);
          updateScene(data);

          const delivered = data.boxes.filter((b) => b.status === "delivered").length;
          setDeliveredPerc((delivered / number) * 100);
          setIterations((prev) => prev + 1);

          const movingRobots = data.robots.filter((r) => r.stopped !== "stop").length;
          if (movingRobots === 0) {
            handleStop();
          }
        });
    }, 300 / simSpeed);
  };

  const handleStop = () => {
    setRunning(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const initializeScene = (data) => {
    const { boxes, robots, storages } = objects.current;
    const scene = sceneRef.current;

    boxes.forEach((box) => scene.remove(box));
    robots.forEach((robot) => scene.remove(robot));
    storages.forEach((storage) => scene.remove(storage));

    objects.current.boxes = data.boxes.map((box) => {
      const geometry = new THREE.BoxGeometry(box.width / 6.4, box.height / 6.4, box.depth / 6.4);
      const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(box.pos[0] * 5, box.height / 13 + 0.5, box.pos[1] * 5);
      scene.add(mesh);
      return mesh;
    });

    objects.current.robots = data.robots.map((robot) => {
      const geometry = new THREE.BoxGeometry(5, 5, 5);
      const material = new THREE.MeshStandardMaterial({ color: 0x0000ff });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(robot.pos[0] * 5, 2.5, robot.pos[1] * 5);
      scene.add(mesh);
      return mesh;
    });

    objects.current.storages = data.storages.map((storage) => {
      const geometry = new THREE.BoxGeometry(storage.width / 6.4, storage.height / 6.4, storage.depth / 6.4);
      const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(storage.pos[0] * 5, storage.height / 13 + 0.5, storage.pos[1] * 5.72);
      scene.add(mesh);
      return mesh;
    });
  };

  const updateScene = (data) => {
    const { boxes, robots, storages } = objects.current;

    data.boxes.forEach((box, i) => {
      boxes[i].position.set(box.pos[0] * 5, box.height / 13 + 0.5, box.pos[1] * 5);
    });

    data.robots.forEach((robot, i) => {
      robots[i].position.set(robot.pos[0] * 5, 2.5, robot.pos[1] * 5);
    });

    data.storages.forEach((storage, i) => {
      storages[i].position.set(storage.pos[0] * 5, storage.height / 13 + 0.5, storage.pos[1] * 5.72);
    });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewBox({ ...newBox, [name]: value });
  };

  const addBox = () => {
    fetch('http://localhost:8000/boxes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newBox),
    })
      .then((response) => response.json())
      .then((data) => {
        setDynamicBoxes((prev) => [...prev, data.box]);
        setNewBox({ name: '', width: '', height: '', depth: '', weight: '' });
      });
  };

  const deleteBox = (name) => {
    fetch(`http://localhost:8000/boxes/${name}`, { method: 'DELETE' })
      .then((response) => response.json())
      .then((data) => setDynamicBoxes(data.remaining_boxes));
  };

  useEffect(() => {
    fetch('http://localhost:8000/boxes')
      .then((response) => response.json())
      .then((data) => setDynamicBoxes(data.boxes));
  }, []);

  return (
    <div style={{ position: 'relative' }}>
      <div ref={mountRef} style={{ width: '100vw', height: '100vh' }}></div>
      <div
        className="controls"
        style={{
          position: 'absolute',
          top: '10px',
          left: '10px',
          backgroundColor: 'black',
          color: 'white',
          padding: '10px',
          paddingRight: '30px',
          paddingLeft: '30px',
          borderRadius: '5px',
          boxShadow: '0 0 10px rgba(0, 0, 0, 1)',
          maxWidth: '300px',
        }}
      >
        <button
          onClick={setup}
          disabled={running}
          style={{
            backgroundColor: running ? '#cccccc' : 'white', // Más oscuro si está deshabilitado
            color: running ? '#666666' : 'black',
            padding: '5px 10px',
            border: 'none',
            borderRadius: '3px',
            margin: '5px 0',
            cursor: running ? 'not-allowed' : 'pointer', // Cambiar cursor si está deshabilitado
          }}
        >
          Preparar
        </button>
        <button
          onClick={handleStart}
          disabled={running}
          style={{
            backgroundColor: running ? '#cccccc' : 'white',
            color: running ? '#666666' : 'black',
            padding: '5px 10px',
            border: 'none',
            borderRadius: '3px',
            margin: '5px 0',
            cursor: running ? 'not-allowed' : 'pointer',
          }}
        >
          Empezar
        </button>
        <button
          onClick={handleStop}
          disabled={!running}
          style={{
            backgroundColor: !running ? '#cccccc' : 'white',
            color: !running ? '#666666' : 'black',
            padding: '5px 10px',
            border: 'none',
            borderRadius: '3px',
            margin: '5px 0',
            cursor: !running ? 'not-allowed' : 'pointer',
          }}
        >
          Parar
        </button>
        <p>Iteraciones: {iterations}</p>
        <p>Porcentaje entregado: {deliveredPerc}%</p>
        <h3>Gestión de Cajas</h3>
        <input
          name="name"
          value={newBox.name}
          onChange={handleInputChange}
          placeholder="Nombre"
          style={{
            backgroundColor: 'white',
            color: 'black',
            padding: '5px',
            border: 'none',
            borderRadius: '3px',
            marginBottom: '5px',
            width: '100%',
          }}
        />
        <input
          name="width"
          value={newBox.width}
          onChange={handleInputChange}
          placeholder="Ancho"
          style={{
            backgroundColor: 'white',
            color: 'black',
            padding: '5px',
            border: 'none',
            borderRadius: '3px',
            marginBottom: '5px',
            width: '100%',
          }}
        />
        <input
          name="height"
          value={newBox.height}
          onChange={handleInputChange}
          placeholder="Alto"
          style={{
            backgroundColor: 'white',
            color: 'black',
            padding: '5px',
            border: 'none',
            borderRadius: '3px',
            marginBottom: '5px',
            width: '100%',
          }}
        />
        <input
          name="depth"
          value={newBox.depth}
          onChange={handleInputChange}
          placeholder="Largo"
          style={{
            backgroundColor: 'white',
            color: 'black',
            padding: '5px',
            border: 'none',
            borderRadius: '3px',
            marginBottom: '5px',
            width: '100%',
          }}
        />
        <input
          name="weight"
          value={newBox.weight}
          onChange={handleInputChange}
          placeholder="Peso"
          style={{
            backgroundColor: 'white',
            color: 'black',
            padding: '5px',
            border: 'none',
            borderRadius: '3px',
            marginBottom: '5px',
            width: '100%',
          }}
        />
        <button
          onClick={addBox}
          disabled={running}
          style={{
            backgroundColor: 'white',
            color: 'black',
            padding: '5px 10px',
            border: 'none',
            borderRadius: '3px',
            cursor: 'pointer',
          }}
        >
          Agregar Caja
        </button>
        <h4>Lista de Cajas</h4>
        <ul>
          {dynamicBoxes.map((box) => (
            <li key={box.name}>
              {box.name} - {box.width}x{box.height}x{box.depth}
              <button
                onClick={() => deleteBox(box.name)}
                style={{
                  backgroundColor: 'white',
                  color: 'black',
                  padding: '3px 5px',
                  border: 'none',
                  borderRadius: '3px',
                  marginLeft: '10px',
                  cursor: 'pointer',
                }}
              >
                Eliminar
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;
