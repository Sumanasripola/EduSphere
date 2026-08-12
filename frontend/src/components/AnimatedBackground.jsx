import Particles from "react-tsparticles";

export default function AnimatedBackground() {
  return (
    <div className="absolute inset-0 -z-10 pointer-events-none">
      <Particles
        options={{
          fpsLimit: 60,
          particles: {
            number: { value: 60 },
            color: { value: "#6366f1" },
            links: {
              enable: true,
              color: "#6366f1",
              distance: 150
            },
            move: {
              enable: true,
              speed: 1
            },
            opacity: { value: 0.5 },
            size: { value: { min: 1, max: 3 } }
          }
        }}
      />
    </div>
  );
}