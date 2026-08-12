import Lottie from "lottie-react";
import animationData from "../assets/document-ai.json";

export default function DocumentAnimation() {
  return (
    <div className="w-[500px] mx-auto">
      <Lottie
        animationData={animationData}
        loop={true}
      />
    </div>
  );
}