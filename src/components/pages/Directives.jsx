import React from "react";

const directives = [
  {
    title: "Clinical Documentation",
    points: [
      "Follow SOAP format",
      "Use structured headings",
      "Highlight key symptoms"
    ]
  },
  {
    title: "Safety & Accuracy",
    points: [
      "Avoid diagnosis without enough data",
      "Flag emergency symptoms",
      "Suggest professional consultation"
    ]
  },
  {
    title: "AI Behavior",
    points: [
      "Be neutral and unbiased",
      "Ask follow-up questions",
      "Do not assume patient history"
    ]
  },
  {
    title: "Privacy",
    points: [
      "Do not store sensitive data",
      "Protect patient identity",
      "Follow data protection practices"
    ]
  }
];

const Directives = () => {
  return (
    <div className="p-8 min-h-screen bg-gray-50">
      <h1 className="text-3xl font-bold mb-6">System Directives</h1>

      <div className="grid md:grid-cols-2 gap-6">
        {directives.map((section, index) => (
          <div key={index} className="bg-white p-5 rounded-xl shadow">
            <h2 className="text-xl font-semibold mb-3">
              {section.title}
            </h2>

            <ul className="list-disc pl-5 text-gray-700">
              {section.points.map((point, i) => (
                <li key={i}>{point}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Directives;