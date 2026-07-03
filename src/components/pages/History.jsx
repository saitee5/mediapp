import React from "react";

const mockHistory = [
  {
    patient: "Selena Gomez",
    issue: "Kidney transplant",
    date: "2 July, 4:30 PM",
    status: "Completed",
  },
  {
    patient: "Justin Bieber",
    issue: "Hypertension",
    date: "1 July, 2:00 PM",
    status: "Draft",
  },
];

const History = () => {
  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Consultation History</h1>

      <div className="space-y-4">
        {mockHistory.map((item, index) => (
          <div
            key={index}
            className="bg-white p-5 rounded-xl shadow flex justify-between items-center"
          >
            <div>
              <h2 className="text-lg font-semibold">{item.patient}</h2>
              <p className="text-sm text-gray-600">{item.issue}</p>
              <p className="text-xs text-gray-400">{item.date}</p>
            </div>

            <span
              className={`text-xs font-bold px-3 py-1 rounded-full ${
                item.status === "Completed"
                  ? "bg-green-100 text-green-600"
                  : "bg-yellow-100 text-yellow-600"
              }`}
            >
              {item.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default History;