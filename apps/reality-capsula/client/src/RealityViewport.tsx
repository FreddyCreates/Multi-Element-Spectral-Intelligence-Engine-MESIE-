import { Canvas } from "@react-three/fiber";
import { OrbitControls, Stars } from "@react-three/drei";
import { RealityMesh } from "./RealityMesh";

type Props = { coreId: string; phiScore: number };

export function RealityViewport({ coreId, phiScore }: Props) {
  return (
    <div className="viewport-wrap">
      <Canvas camera={{ position: [0, 1.4, 5.5], fov: 48 }}>
        <color attach="background" args={["#050810"]} />
        <fog attach="fog" args={["#050810", 8, 22]} />
        <ambientLight intensity={0.45} color="#334466" />
        <directionalLight position={[4, 6, 3]} intensity={1.1} />
        <pointLight position={[-2, 2, 2]} intensity={0.7} color="#3d8bfd" />
        <Stars radius={40} depth={30} count={1200} factor={3} fade speed={0.5} />
        <RealityMesh coreId={coreId} phiScore={phiScore} />
        <OrbitControls enableDamping dampingFactor={0.08} />
      </Canvas>
      <div style={{ position: "absolute", top: 16, left: 16, pointerEvents: "none" }}>
        <span className="badge">REACT · THREE · R3F</span>
      </div>
    </div>
  );
}
