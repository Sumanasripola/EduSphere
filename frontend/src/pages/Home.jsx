import Hero from "../components/Hero";
import FeatureCards from "../components/FeatureCards";

export default function Home({ onNavigate }) {
  return (
    <>
      <Hero onGetStarted={() => onNavigate("dashboard")} />
      <FeatureCards />
    </>
  );
}