import { useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";

const PHI = 0.6180339887498948;

const SHAPES: Record<string, () => THREE.BufferGeometry> = {
  core_geometrica: () => new THREE.IcosahedronGeometry(1.3, 3),
  core_spatialis: () => new THREE.TorusKnotGeometry(0.75, 0.22, 128, 16),
  core_datavis: () => new THREE.BoxGeometry(1.6, 1.6, 1.6, 4, 4, 4),
  core_sonora: () => new THREE.SphereGeometry(1.1, 32, 32),
  core_kinetica: () => new THREE.OctahedronGeometry(1.4, 2),
  default: () => new THREE.DodecahedronGeometry(1.2, 1),
};

function phiColors(geo: THREE.BufferGeometry) {
  const pos = geo.attributes.position;
  const colors: number[] = [];
  for (let i = 0; i < pos.count; i++) {
    const t = i / pos.count;
    colors.push(PHI * (0.2 + t), 0.35 + t * 0.3, 1.0 - t * PHI * 0.5);
  }
  geo.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
}

type Props = { coreId: string; phiScore: number };

export function RealityMesh({ coreId, phiScore }: Props) {
  const ref = useRef<THREE.Mesh>(null);
  const geo = useMemo(() => {
    const factory = SHAPES[coreId] || SHAPES.default;
    const g = factory();
    phiColors(g);
    return g;
  }, [coreId]);

  useFrame((_, dt) => {
    if (!ref.current) return;
    ref.current.rotation.y += dt * 0.35;
    ref.current.rotation.x = Math.sin(performance.now() * 0.0003) * 0.12;
    const s = 1 + phiScore * 0.15;
    ref.current.scale.setScalar(s);
  });

  return (
    <mesh ref={ref} geometry={geo}>
      <meshStandardMaterial
        vertexColors
        metalness={0.55}
        roughness={0.28}
        emissive="#0a1628"
        emissiveIntensity={0.35 + phiScore * 0.3}
      />
    </mesh>
  );
}
