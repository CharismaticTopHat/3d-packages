import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

import './App.css';

function App() {
  const mountRef = useRef(null);

  // Estados para simulación
  const [sliderGridSize, setSliderGridSize] = useState(80); // Tamaño de la cuadrícula
  const [number, setNumber] = useState(40); // Número de cajas
  const [simSpeed, setSimSpeed] = useState(2); // Velocidad de simulación
  const [boxes, setBoxes] = useState([]); // Estado de las cajas
  const [robots, setRobots] = useState([]); // Estado de los robots
  const [storages, setStorages] = useState([]); // Estado de los almacenamientos
  const [location, setLocation] = useState(""); // Ubicación del backend
  const [iterations, setIterations] = useState(0); // Número de iteraciones
  const [deliveredPerc, setDeliveredPerc] = useState(0); // Porcentaje de cajas entregadas
  const [running, setRunning] = useState(false); // Estado de ejecución

  // Referencias para Three.js
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const objects = useRef({ boxes: [], robots: [], storages: [] });

  useEffect(() => {
    // Configuración inicial de Three.js
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xffffff);

    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1010);
    camera.position.set(sliderGridSize * 5, sliderGridSize * 2, sliderGridSize * 5);

    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    mountRef.current.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    // Agregar cuadrícula
    // Calcular tamaño del grid y divisiones
    const gridSize = sliderGridSize * 5; // Tamaño total del grid basado en el tamaño de las celdas
    const divisions = sliderGridSize; // Una división por cada celda

    // Crear y posicionar el grid
    const gridHelper = new THREE.GridHelper(gridSize, divisions);
    gridHelper.position.set(gridSize / 2 - 2.5, 0, gridSize / 2 + 2.5); // Centrar el grid
    scene.add(gridHelper);

    // Luces
    const ambientLight = new THREE.AmbientLight(0x404040);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(sliderGridSize * 5, sliderGridSize * 10, sliderGridSize * 5);
    scene.add(ambientLight, directionalLight);

    // Guardar referencias
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
    if (!location) return;

    setRunning(true);
    const interval = setInterval(() => {
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

          const movingRobots = data.robots.filter((r) => r.stopped !== "moving").length;
          if (movingRobots === 0) {
            handleStop();
          }
        });
    }, 300 / simSpeed);

    return () => clearInterval(interval);
  };

  const handleStop = () => {
    setRunning(false);
  };

  const initializeScene = (data) => {
    const { boxes, robots, storages } = objects.current;
    const scene = sceneRef.current;

    // Limpiar objetos existentes
    boxes.forEach((box) => scene.remove(box));
    robots.forEach((robot) => scene.remove(robot));
    storages.forEach((storage) => scene.remove(storage));

    objects.current.boxes = data.boxes.map((box) => {
      const geometry = new THREE.BoxGeometry(5, 5, 5);
      const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(box.pos[0] * 5, 2.5, box.pos[1] * 5);
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
      const geometry = new THREE.BoxGeometry(10, 10, 10);
      const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(storage.pos[0] * 5, 2.5, storage.pos[1] * 5);
      scene.add(mesh);
      return mesh;
    });
  };

  const updateScene = (data) => {
    const { boxes, robots, storages } = objects.current;

    data.boxes.forEach((box, i) => {
      boxes[i].position.set(box.pos[0] * 5, 2.5, box.pos[1] * 5);
    });

    data.robots.forEach((robot, i) => {
      robots[i].position.set(robot.pos[0] * 5, 2.5, robot.pos[1] * 5);
    });

    data.storages.forEach((storage, i) => {
      storages[i].position.set(storage.pos[0] * 5, 5, storage.pos[1] * 5);
    });
  };

  return (
    <>
      <style>
        {`
          .controls {
            margin: 20px;
          }
        `}
      </style>
      <div ref={mountRef} style={{ width: '100vw', height: '80vh' }}></div>
      <div className="controls">
        <button onClick={setup} disabled={running}>Setup</button>
        <button onClick={handleStart} disabled={running}>Start</button>
        <button onClick={handleStop} disabled={!running}>Stop</button>
        <p>Iteraciones: {iterations}</p>
        <p>Porcentaje entregado: {deliveredPerc}%</p>
      </div>
    </>
  );
}

export default App;
