/**
 * Brain3D — Interactive Three.js 3D Brain Model
 *
 * Renders 52 anatomical brain structures as positioned 3D shapes
 * in a sagittal-to-3D mapping. Each region is clickable and color-coded
 * by category (cortical, subcortical, limbic, brainstem, cerebellar,
 * white_matter, specialized).
 *
 * Kernel data is computed live — F, ω, IC, Δ, S, C per structure.
 */

import * as THREE from 'three';

// ── Category Colors (hex) ────────────────────────────────────────

const CAT_HEX: Record<string, number> = {
  cortical: 0x3b82f6,
  subcortical: 0xa855f7,
  limbic: 0x22c55e,
  brainstem: 0xf59e0b,
  cerebellar: 0x06b6d4,
  white_matter: 0xec4899,
  specialized: 0xf43647,
};

// ── Brain Region 3D Layout ───────────────────────────────────────
// Positions in normalized [-1, 1] brain space (sagittal view → 3D):
//   x = left-right (0 = midline)
//   y = superior-inferior
//   z = anterior-posterior

interface RegionDef {
  name: string;
  category: string;
  pos: [number, number, number]; // [x, y, z]
  scale: [number, number, number]; // [sx, sy, sz]
  shape: 'sphere' | 'ellipsoid' | 'capsule';
}

const REGION_DEFS: RegionDef[] = [
  // ── Cortical (8) ───────────────────────────────────────────────
  { name: 'frontal_cortex', category: 'cortical', pos: [0, 0.55, 0.65], scale: [0.55, 0.35, 0.35], shape: 'ellipsoid' },
  { name: 'parietal_cortex', category: 'cortical', pos: [0, 0.65, -0.05], scale: [0.5, 0.25, 0.3], shape: 'ellipsoid' },
  { name: 'occipital_cortex', category: 'cortical', pos: [0, 0.35, -0.65], scale: [0.35, 0.3, 0.25], shape: 'ellipsoid' },
  { name: 'temporal_cortex', category: 'cortical', pos: [0.45, -0.1, 0.2], scale: [0.2, 0.2, 0.4], shape: 'ellipsoid' },
  { name: 'insular_cortex', category: 'cortical', pos: [0.3, 0.15, 0.2], scale: [0.08, 0.12, 0.15], shape: 'ellipsoid' },
  { name: 'entorhinal_cortex', category: 'cortical', pos: [0.25, -0.2, 0.35], scale: [0.08, 0.06, 0.08], shape: 'sphere' },
  { name: 'prefrontal_dorsolateral', category: 'cortical', pos: [0.3, 0.6, 0.55], scale: [0.2, 0.15, 0.15], shape: 'ellipsoid' },
  { name: 'somatosensory_cortex', category: 'cortical', pos: [0.15, 0.6, 0.05], scale: [0.15, 0.2, 0.12], shape: 'ellipsoid' },

  // ── Subcortical (7) ────────────────────────────────────────────
  { name: 'thalamus', category: 'subcortical', pos: [0.08, 0.15, -0.05], scale: [0.15, 0.1, 0.12], shape: 'ellipsoid' },
  { name: 'caudate', category: 'subcortical', pos: [0.15, 0.35, 0.15], scale: [0.05, 0.12, 0.06], shape: 'ellipsoid' },
  { name: 'putamen', category: 'subcortical', pos: [0.22, 0.2, 0.1], scale: [0.06, 0.1, 0.08], shape: 'ellipsoid' },
  { name: 'globus_pallidus', category: 'subcortical', pos: [0.18, 0.18, 0.05], scale: [0.04, 0.07, 0.05], shape: 'ellipsoid' },
  { name: 'subthalamic_nucleus', category: 'subcortical', pos: [0.1, 0.05, 0.0], scale: [0.03, 0.02, 0.03], shape: 'sphere' },
  { name: 'nucleus_accumbens', category: 'subcortical', pos: [0.12, 0.08, 0.3], scale: [0.04, 0.03, 0.04], shape: 'sphere' },
  { name: 'claustrum', category: 'subcortical', pos: [0.28, 0.2, 0.15], scale: [0.02, 0.12, 0.1], shape: 'ellipsoid' },

  // ── Limbic (7) ─────────────────────────────────────────────────
  { name: 'hippocampus_ca1', category: 'limbic', pos: [0.2, -0.05, -0.05], scale: [0.06, 0.04, 0.1], shape: 'ellipsoid' },
  { name: 'hippocampus_ca23', category: 'limbic', pos: [0.2, -0.05, -0.15], scale: [0.05, 0.04, 0.08], shape: 'ellipsoid' },
  { name: 'amygdala_lateral', category: 'limbic', pos: [0.22, -0.08, 0.12], scale: [0.05, 0.05, 0.04], shape: 'sphere' },
  { name: 'amygdala_basal', category: 'limbic', pos: [0.22, -0.12, 0.12], scale: [0.04, 0.04, 0.04], shape: 'sphere' },
  { name: 'cingulate_cortex', category: 'limbic', pos: [0.0, 0.5, 0.15], scale: [0.06, 0.04, 0.35], shape: 'ellipsoid' },
  { name: 'septal_nuclei', category: 'limbic', pos: [0.0, 0.15, 0.3], scale: [0.04, 0.04, 0.03], shape: 'sphere' },
  { name: 'mammillary_body', category: 'limbic', pos: [0.03, -0.12, 0.05], scale: [0.03, 0.03, 0.03], shape: 'sphere' },

  // ── Brainstem (7) ──────────────────────────────────────────────
  { name: 'midbrain', category: 'brainstem', pos: [0, -0.15, -0.2], scale: [0.08, 0.06, 0.08], shape: 'ellipsoid' },
  { name: 'pons', category: 'brainstem', pos: [0, -0.25, -0.18], scale: [0.1, 0.07, 0.1], shape: 'ellipsoid' },
  { name: 'medulla', category: 'brainstem', pos: [0, -0.38, -0.2], scale: [0.07, 0.09, 0.07], shape: 'ellipsoid' },
  { name: 'substantia_nigra', category: 'brainstem', pos: [0.06, -0.12, -0.18], scale: [0.04, 0.02, 0.04], shape: 'sphere' },
  { name: 'red_nucleus', category: 'brainstem', pos: [0.03, -0.1, -0.2], scale: [0.025, 0.025, 0.025], shape: 'sphere' },
  { name: 'locus_coeruleus', category: 'brainstem', pos: [0.04, -0.22, -0.22], scale: [0.02, 0.015, 0.02], shape: 'sphere' },
  { name: 'raphe_nuclei', category: 'brainstem', pos: [0, -0.2, -0.24], scale: [0.02, 0.08, 0.02], shape: 'ellipsoid' },

  // ── Cerebellar (6) ─────────────────────────────────────────────
  { name: 'cerebellum_anterior', category: 'cerebellar', pos: [0, -0.15, -0.5], scale: [0.3, 0.12, 0.12], shape: 'ellipsoid' },
  { name: 'cerebellum_posterior', category: 'cerebellar', pos: [0, -0.25, -0.55], scale: [0.35, 0.15, 0.15], shape: 'ellipsoid' },
  { name: 'vermis', category: 'cerebellar', pos: [0, -0.2, -0.52], scale: [0.05, 0.1, 0.1], shape: 'ellipsoid' },
  { name: 'dentate_nucleus', category: 'cerebellar', pos: [0.15, -0.2, -0.48], scale: [0.04, 0.04, 0.04], shape: 'sphere' },
  { name: 'cerebellar_wm', category: 'cerebellar', pos: [0, -0.18, -0.48], scale: [0.2, 0.08, 0.08], shape: 'ellipsoid' },
  { name: 'cerebellar_peduncles', category: 'cerebellar', pos: [0.1, -0.18, -0.38], scale: [0.06, 0.04, 0.06], shape: 'ellipsoid' },

  // ── White Matter (8) ───────────────────────────────────────────
  { name: 'corpus_callosum', category: 'white_matter', pos: [0, 0.38, 0.05], scale: [0.08, 0.03, 0.35], shape: 'ellipsoid' },
  { name: 'corticospinal_tract', category: 'white_matter', pos: [0.08, 0.0, -0.1], scale: [0.03, 0.25, 0.03], shape: 'ellipsoid' },
  { name: 'arcuate_fasciculus', category: 'white_matter', pos: [0.35, 0.35, 0.1], scale: [0.03, 0.03, 0.2], shape: 'ellipsoid' },
  { name: 'uncinate_fasciculus', category: 'white_matter', pos: [0.3, 0.05, 0.35], scale: [0.03, 0.03, 0.12], shape: 'ellipsoid' },
  { name: 'fornix', category: 'white_matter', pos: [0, 0.25, 0.05], scale: [0.03, 0.12, 0.04], shape: 'ellipsoid' },
  { name: 'internal_capsule', category: 'white_matter', pos: [0.15, 0.2, 0.0], scale: [0.04, 0.15, 0.04], shape: 'ellipsoid' },
  { name: 'anterior_commissure', category: 'white_matter', pos: [0, 0.1, 0.2], scale: [0.12, 0.02, 0.02], shape: 'ellipsoid' },
  { name: 'cingulum_bundle', category: 'white_matter', pos: [0.06, 0.45, 0.1], scale: [0.03, 0.03, 0.3], shape: 'ellipsoid' },

  // ── Specialized (9) ────────────────────────────────────────────
  { name: 'hypothalamus', category: 'specialized', pos: [0, 0.02, 0.1], scale: [0.06, 0.05, 0.06], shape: 'ellipsoid' },
  { name: 'thalamic_pulvinar', category: 'specialized', pos: [0.1, 0.15, -0.18], scale: [0.06, 0.04, 0.05], shape: 'ellipsoid' },
  { name: 'lateral_geniculate', category: 'specialized', pos: [0.15, 0.05, -0.12], scale: [0.03, 0.03, 0.03], shape: 'sphere' },
  { name: 'medial_geniculate', category: 'specialized', pos: [0.12, 0.03, -0.15], scale: [0.025, 0.025, 0.025], shape: 'sphere' },
  { name: 'mammillothalamic_tract', category: 'specialized', pos: [0.02, 0.0, 0.02], scale: [0.015, 0.08, 0.015], shape: 'ellipsoid' },
  { name: 'pineal_gland', category: 'specialized', pos: [0, 0.2, -0.22], scale: [0.025, 0.025, 0.025], shape: 'sphere' },
  { name: 'choroid_plexus', category: 'specialized', pos: [0.05, 0.3, -0.05], scale: [0.04, 0.02, 0.15], shape: 'ellipsoid' },
  { name: 'area_postrema', category: 'specialized', pos: [0, -0.35, -0.22], scale: [0.02, 0.015, 0.02], shape: 'sphere' },
  { name: 'suprachiasmatic_nucleus', category: 'specialized', pos: [0, 0.0, 0.15], scale: [0.02, 0.015, 0.02], shape: 'sphere' },
];

// ── Brain3D class ────────────────────────────────────────────────

export interface Brain3DOptions {
  container: HTMLElement;
  onRegionClick?: (regionName: string) => void;
  onRegionHover?: (regionName: string | null) => void;
}

export class Brain3D {
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  private regionMeshes: Map<string, THREE.Mesh> = new Map();
  private brainGroup: THREE.Group;
  private raycaster = new THREE.Raycaster();
  private mouse = new THREE.Vector2();
  private hoveredMesh: THREE.Mesh | null = null;
  private selectedName: string | null = null;
  private autoRotate = true;
  private isDragging = false;
  private prevMouse = { x: 0, y: 0 };
  private rotationSpeed = { x: 0, y: 0 };
  private animFrame = 0;
  private onRegionClick?: (name: string) => void;
  private onRegionHover?: (name: string | null) => void;
  private container: HTMLElement;

  constructor(opts: Brain3DOptions) {
    this.container = opts.container;
    this.onRegionClick = opts.onRegionClick;
    this.onRegionHover = opts.onRegionHover;

    // Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x020617);

    // Camera
    const aspect = opts.container.clientWidth / opts.container.clientHeight;
    this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 100);
    this.camera.position.set(1.8, 0.6, 1.8);
    this.camera.lookAt(0, 0.1, 0);

    // Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(opts.container.clientWidth, opts.container.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    opts.container.appendChild(this.renderer.domElement);

    // Lights
    const ambient = new THREE.AmbientLight(0x334155, 1.2);
    this.scene.add(ambient);
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(3, 4, 2);
    this.scene.add(dirLight);
    const backLight = new THREE.DirectionalLight(0x4488ff, 0.3);
    backLight.position.set(-2, -1, -3);
    this.scene.add(backLight);

    // Brain group (all regions)
    this.brainGroup = new THREE.Group();
    this.scene.add(this.brainGroup);

    // Build outline
    this.buildOutline();

    // Build regions (mirrored for bilateral)
    this.buildRegions();

    // Events
    this.setupEvents();

    // Start animation
    this.animate();
  }

  private buildOutline(): void {
    // Semi-transparent cerebral outline (two hemispheres)
    const brainGeo = new THREE.SphereGeometry(0.85, 32, 24);
    brainGeo.scale(0.65, 0.55, 0.75);
    const brainMat = new THREE.MeshPhongMaterial({
      color: 0x1e293b,
      transparent: true,
      opacity: 0.08,
      wireframe: false,
      side: THREE.DoubleSide,
      depthWrite: false,
    });
    const outline = new THREE.Mesh(brainGeo, brainMat);
    outline.position.set(0, 0.2, 0);
    this.brainGroup.add(outline);

    // Spinal cord stump
    const spinalGeo = new THREE.CylinderGeometry(0.04, 0.03, 0.3, 8);
    const spinalMat = new THREE.MeshPhongMaterial({
      color: 0x334155,
      transparent: true,
      opacity: 0.15,
    });
    const spinal = new THREE.Mesh(spinalGeo, spinalMat);
    spinal.position.set(0, -0.5, -0.2);
    this.brainGroup.add(spinal);
  }

  private buildRegions(): void {
    for (const def of REGION_DEFS) {
      const color = CAT_HEX[def.category] ?? 0xffffff;

      // Create geometry
      const geo = new THREE.SphereGeometry(1, 16, 12);
      geo.scale(def.scale[0], def.scale[1], def.scale[2]);

      const mat = new THREE.MeshPhongMaterial({
        color,
        transparent: true,
        opacity: 0.55,
        emissive: new THREE.Color(color),
        emissiveIntensity: 0.15,
        shininess: 60,
      });

      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(def.pos[0], def.pos[1], def.pos[2]);
      mesh.userData = { regionName: def.name, category: def.category };
      this.brainGroup.add(mesh);
      this.regionMeshes.set(def.name, mesh);

      // Mirror for bilateral structures (those not on midline)
      if (Math.abs(def.pos[0]) > 0.01) {
        const mirrorMat = mat.clone();
        const mirrorMesh = new THREE.Mesh(geo.clone(), mirrorMat);
        mirrorMesh.position.set(-def.pos[0], def.pos[1], def.pos[2]);
        mirrorMesh.userData = { regionName: def.name, category: def.category, mirror: true };
        this.brainGroup.add(mirrorMesh);
      }
    }
  }

  private setupEvents(): void {
    const canvas = this.renderer.domElement;

    canvas.addEventListener('mousemove', (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      if (this.isDragging) {
        const dx = e.clientX - this.prevMouse.x;
        const dy = e.clientY - this.prevMouse.y;
        this.rotationSpeed.x = dx * 0.005;
        this.rotationSpeed.y = dy * 0.005;
        this.brainGroup.rotation.y += this.rotationSpeed.x;
        this.brainGroup.rotation.x += this.rotationSpeed.y;
        this.brainGroup.rotation.x = Math.max(-Math.PI / 3, Math.min(Math.PI / 3, this.brainGroup.rotation.x));
        this.prevMouse = { x: e.clientX, y: e.clientY };
      }
    });

    canvas.addEventListener('mousedown', (e: MouseEvent) => {
      this.isDragging = true;
      this.autoRotate = false;
      this.prevMouse = { x: e.clientX, y: e.clientY };
    });

    canvas.addEventListener('mouseup', () => {
      this.isDragging = false;
    });

    canvas.addEventListener('mouseleave', () => {
      this.isDragging = false;
    });

    canvas.addEventListener('click', () => {
      if (Math.abs(this.rotationSpeed.x) > 0.02 || Math.abs(this.rotationSpeed.y) > 0.02) return;
      this.raycaster.setFromCamera(this.mouse, this.camera);
      const intersects = this.raycaster.intersectObjects(this.brainGroup.children, false);
      for (const hit of intersects) {
        const name = hit.object.userData?.regionName;
        if (name) {
          this.selectRegion(name);
          this.onRegionClick?.(name);
          break;
        }
      }
    });

    canvas.addEventListener('wheel', (e: WheelEvent) => {
      e.preventDefault();
      const dir = new THREE.Vector3();
      this.camera.getWorldDirection(dir);
      this.camera.position.addScaledVector(dir, -e.deltaY * 0.002);
      // Clamp distance
      const dist = this.camera.position.length();
      if (dist < 1.2) this.camera.position.setLength(1.2);
      if (dist > 5) this.camera.position.setLength(5);
    }, { passive: false });

    // Resize
    const ro = new ResizeObserver(() => {
      const w = this.container.clientWidth;
      const h = this.container.clientHeight;
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h);
    });
    ro.observe(this.container);
  }

  private animate = (): void => {
    this.animFrame = requestAnimationFrame(this.animate);

    // Auto-rotate
    if (this.autoRotate) {
      this.brainGroup.rotation.y += 0.003;
    }

    // Gentle float
    this.brainGroup.position.y = Math.sin(Date.now() * 0.001) * 0.015;

    // Raycast for hover
    this.raycaster.setFromCamera(this.mouse, this.camera);
    const intersects = this.raycaster.intersectObjects(this.brainGroup.children, false);

    // Reset previous hover
    if (this.hoveredMesh) {
      const mat = this.hoveredMesh.material as THREE.MeshPhongMaterial;
      if (this.hoveredMesh.userData.regionName !== this.selectedName) {
        mat.emissiveIntensity = 0.15;
        mat.opacity = 0.55;
      }
      this.hoveredMesh = null;
    }

    for (const hit of intersects) {
      const name = hit.object.userData?.regionName;
      if (name) {
        this.hoveredMesh = hit.object as THREE.Mesh;
        const mat = this.hoveredMesh.material as THREE.MeshPhongMaterial;
        mat.emissiveIntensity = 0.5;
        mat.opacity = 0.8;
        this.onRegionHover?.(name);
        this.renderer.domElement.style.cursor = 'pointer';
        break;
      }
    }

    if (!this.hoveredMesh) {
      this.onRegionHover?.(null);
      this.renderer.domElement.style.cursor = 'grab';
    }

    // Dampen rotation
    if (!this.isDragging) {
      this.rotationSpeed.x *= 0.95;
      this.rotationSpeed.y *= 0.95;
      this.brainGroup.rotation.y += this.rotationSpeed.x;
      this.brainGroup.rotation.x += this.rotationSpeed.y;
      this.brainGroup.rotation.x = Math.max(-Math.PI / 3, Math.min(Math.PI / 3, this.brainGroup.rotation.x));
    }

    this.renderer.render(this.scene, this.camera);
  };

  selectRegion(name: string): void {
    // Deselect previous
    if (this.selectedName) {
      const prev = this.regionMeshes.get(this.selectedName);
      if (prev) {
        const mat = prev.material as THREE.MeshPhongMaterial;
        mat.emissiveIntensity = 0.15;
        mat.opacity = 0.55;
      }
    }

    this.selectedName = name;
    const mesh = this.regionMeshes.get(name);
    if (mesh) {
      const mat = mesh.material as THREE.MeshPhongMaterial;
      mat.emissiveIntensity = 0.7;
      mat.opacity = 0.9;
    }

    // Dim unrelated regions
    this.regionMeshes.forEach((m, n) => {
      if (n !== name) {
        const mat = m.material as THREE.MeshPhongMaterial;
        mat.opacity = 0.2;
        mat.emissiveIntensity = 0.05;
      }
    });
    // Also dim mirror meshes
    this.brainGroup.children.forEach(child => {
      if (child.userData?.mirror && child.userData.regionName !== name) {
        const mat = (child as THREE.Mesh).material as THREE.MeshPhongMaterial;
        if (mat.opacity !== undefined) {
          mat.opacity = 0.2;
          mat.emissiveIntensity = 0.05;
        }
      }
    });
  }

  clearSelection(): void {
    this.selectedName = null;
    this.regionMeshes.forEach(m => {
      const mat = m.material as THREE.MeshPhongMaterial;
      mat.opacity = 0.55;
      mat.emissiveIntensity = 0.15;
    });
    this.brainGroup.children.forEach(child => {
      if (child.userData?.mirror) {
        const mat = (child as THREE.Mesh).material as THREE.MeshPhongMaterial;
        if (mat.opacity !== undefined) {
          mat.opacity = 0.55;
          mat.emissiveIntensity = 0.15;
        }
      }
    });
  }

  resetView(): void {
    this.autoRotate = true;
    this.brainGroup.rotation.set(0, 0, 0);
    this.camera.position.set(1.8, 0.6, 1.8);
    this.camera.lookAt(0, 0.1, 0);
    this.clearSelection();
  }

  dispose(): void {
    cancelAnimationFrame(this.animFrame);
    this.renderer.dispose();
    this.scene.clear();
    this.renderer.domElement.remove();
  }
}
