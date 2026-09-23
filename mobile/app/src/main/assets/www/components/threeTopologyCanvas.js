/**
 * OmniRevive-OS | Three.js WebGL 3D Cyber-Topology & Network Constellation
 * Conforms to: DESIGN.md Specification (Section 4)
 * Visualizes real-time transaction packet routing across global fintech switch nodes.
 */

class ThreeTopologyCanvas {
  constructor(containerId = 'threejs-topology-mount') {
    this.containerId = containerId;
    this.container = document.getElementById(containerId);
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.nodes = [];
    this.packetCurves = [];
    this.particles = null;
    this.mouseX = 0;
    this.mouseY = 0;
    this.targetRotationX = 0;
    this.targetRotationY = 0;
    this.animFrameId = null;
    this.isRunning = false;

    this.nodeMetadata = [
      { name: "ap-south-1 (Mumbai)", color: 0x06b6d4, x: -140, y: 50, z: 0, size: 7 },
      { name: "ap-south-2 (Hyderabad)", color: 0x64748b, x: -90, y: -40, z: -20, size: 5 },
      { name: "NPCI Central (UPI 2.0)", color: 0x10b981, x: 0, y: 80, z: 20, size: 8 },
      { name: "Juspay HyperSDK", color: 0xf59e0b, x: 90, y: 40, z: -10, size: 6 },
      { name: "PhonePe Switch", color: 0x8b5cf6, x: 130, y: -30, z: 10, size: 6 },
      { name: "CRED CAS Engine", color: 0xf43f5e, x: -20, y: -70, z: -15, size: 6 },
      { name: "Stripe Global FX", color: 0x38bdf8, x: 190, y: 70, z: -40, size: 6 }
    ];

    this.init();
  }

  init() {
    if (!this.container || typeof THREE === 'undefined') {
      console.warn('[ThreeTopology] Container or THREE.js not available.');
      return;
    }

    const width = this.container.clientWidth || 800;
    const height = this.container.clientHeight || 300;

    // 1. Scene
    this.scene = new THREE.Scene();

    // 2. Camera
    this.camera = new THREE.PerspectiveCamera(45, width / height, 1, 2000);
    this.camera.position.z = 380;

    // 3. Renderer with alpha transparency & antialiasing
    this.renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.innerHTML = '';
    this.container.appendChild(this.renderer.domElement);

    // 4. Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    this.scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x06b6d4, 2, 800);
    pointLight.position.set(0, 50, 200);
    this.scene.add(pointLight);

    // 5. Build 3D Nodes & Connecting Arcs
    this.buildNodes();
    this.buildArcs();
    this.buildStarfield();

    // 6. Listeners
    window.addEventListener('resize', () => this.onResize());
    this.container.addEventListener('mousemove', (e) => this.onMouseMove(e));

    this.start();
  }

  buildNodes() {
    const nodeGroup = new THREE.Group();

    this.nodeMetadata.forEach((meta) => {
      // Core glowing sphere
      const geometry = new THREE.SphereGeometry(meta.size, 16, 16);
      const material = new THREE.MeshStandardMaterial({
        color: meta.color,
        emissive: meta.color,
        emissiveIntensity: 0.6,
        roughness: 0.2,
        metalness: 0.8
      });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(meta.x, meta.y, meta.z);

      // Outer wireframe halo ring
      const ringGeom = new THREE.RingGeometry(meta.size * 1.3, meta.size * 1.5, 24);
      const ringMat = new THREE.MeshBasicMaterial({
        color: meta.color,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.4
      });
      const ring = new THREE.Mesh(ringGeom, ringMat);
      ring.position.copy(mesh.position);
      ring.rotation.x = Math.PI / 3;

      nodeGroup.add(mesh);
      nodeGroup.add(ring);

      this.nodes.push({ mesh, ring, meta, initialY: meta.y });
    });

    this.scene.add(nodeGroup);
    this.nodeGroup = nodeGroup;
  }

  buildArcs() {
    // Interconnect primary nodes with glowing spline curves
    const connections = [
      [0, 2], // Mumbai -> NPCI
      [2, 3], // NPCI -> Juspay
      [2, 4], // NPCI -> PhonePe
      [0, 5], // Mumbai -> CRED
      [3, 6], // Juspay -> Stripe
      [0, 1]  // Mumbai -> Hyderabad DR
    ];

    const arcGroup = new THREE.Group();

    connections.forEach(([i, j]) => {
      const n1 = this.nodeMetadata[i];
      const n2 = this.nodeMetadata[j];

      const v1 = new THREE.Vector3(n1.x, n1.y, n1.z);
      const v2 = new THREE.Vector3(n2.x, n2.y, n2.z);
      const mid = new THREE.Vector3(
        (v1.x + v2.x) / 2,
        (v1.y + v2.y) / 2 + 30, // Elevated arc apex
        (v1.z + v2.z) / 2 + 20
      );

      const curve = new THREE.QuadraticBezierCurve3(v1, mid, v2);
      const points = curve.getPoints(36);
      const geometry = new THREE.BufferGeometry().setFromPoints(points);

      const material = new THREE.LineBasicMaterial({
        color: 0x06b6d4,
        transparent: true,
        opacity: 0.35,
        linewidth: 1
      });

      const line = new THREE.Line(geometry, material);
      arcGroup.add(line);

      // Packet tracer particle on the curve
      const packetGeom = new THREE.SphereGeometry(2, 8, 8);
      const packetMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
      const packet = new THREE.Mesh(packetGeom, packetMat);
      arcGroup.add(packet);

      this.packetCurves.push({ curve, packet, progress: Math.random(), speed: 0.005 + Math.random() * 0.005 });
    });

    this.scene.add(arcGroup);
    this.arcGroup = arcGroup;
  }

  buildStarfield() {
    const starCount = 180;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(starCount * 3);

    for (let i = 0; i < starCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 600;
      positions[i + 1] = (Math.random() - 0.5) * 350;
      positions[i + 2] = (Math.random() - 0.5) * 300;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const material = new THREE.PointsMaterial({
      color: 0x38bdf8,
      size: 1.5,
      transparent: true,
      opacity: 0.4
    });

    this.particles = new THREE.Points(geometry, material);
    this.scene.add(this.particles);
  }

  onMouseMove(event) {
    const rect = this.container.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    const y = -(((event.clientY - rect.top) / rect.height) * 2 - 1);
    this.targetRotationY = x * 0.25;
    this.targetRotationX = y * 0.15;
  }

  onResize() {
    if (!this.container || !this.renderer || !this.camera) return;
    const width = this.container.clientWidth;
    const height = this.container.clientHeight || 300;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  pulseRandomNode() {
    if (!this.nodes.length) return;
    const randomIndex = Math.floor(Math.random() * this.nodes.length);
    const node = this.nodes[randomIndex];
    node.mesh.scale.set(1.6, 1.6, 1.6);
    setTimeout(() => {
      node.mesh.scale.set(1.0, 1.0, 1.0);
    }, 350);
  }

  start() {
    if (this.isRunning) return;
    this.isRunning = true;
    const animate = () => {
      if (!this.isRunning) return;
      this.animFrameId = requestAnimationFrame(animate);

      // Smooth camera / node rotation damping (Rauno style)
      if (this.nodeGroup) {
        this.nodeGroup.rotation.y += (this.targetRotationY - this.nodeGroup.rotation.y) * 0.05;
        this.nodeGroup.rotation.x += (this.targetRotationX - this.nodeGroup.rotation.x) * 0.05;
      }
      if (this.arcGroup) {
        this.arcGroup.rotation.y = this.nodeGroup.rotation.y;
        this.arcGroup.rotation.x = this.nodeGroup.rotation.x;
      }

      // Gentle floating nodes
      const time = Date.now() * 0.002;
      this.nodes.forEach((item, idx) => {
        item.mesh.position.y = item.initialY + Math.sin(time + idx) * 3;
        item.ring.position.y = item.mesh.position.y;
        item.ring.rotation.z += 0.01;
      });

      // Animate packet pulses along curves
      this.packetCurves.forEach((item) => {
        item.progress += item.speed;
        if (item.progress > 1) item.progress = 0;
        const pos = item.curve.getPoint(item.progress);
        item.packet.position.copy(pos);
      });

      // Drift starfield
      if (this.particles) {
        this.particles.rotation.y += 0.0003;
      }

      this.renderer.render(this.scene, this.camera);
    };

    animate();
  }

  resetCamera() {
    this.targetRotationX = 0;
    this.targetRotationY = 0;
    if (this.nodeGroup) {
      this.nodeGroup.rotation.set(0, 0, 0);
    }
    if (this.arcGroup) {
      this.arcGroup.rotation.set(0, 0, 0);
    }
    if (this.camera) {
      this.camera.position.set(0, 0, 380);
      this.camera.lookAt(0, 0, 0);
    }
  }

  stop() {
    this.isRunning = false;
    if (this.animFrameId) cancelAnimationFrame(this.animFrameId);
  }
}

// Global mounting helper
window.initThreeTopology = function(containerId = 'threejs-topology-mount') {
  if (window._threeTopologyInstance) {
    window._threeTopologyInstance.stop();
  }
  window._threeTopologyInstance = new ThreeTopologyCanvas(containerId);
  return window._threeTopologyInstance;
};
