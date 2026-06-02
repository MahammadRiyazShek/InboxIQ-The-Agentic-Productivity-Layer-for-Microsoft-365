import React from "react";
import Dashboard from "./pages/Dashboard";
import { FluentProvider, webLightTheme } from "@fluentui/react-components";

export default function App() {
  return (
    <FluentProvider theme={webLightTheme}>
      <Dashboard />
    </FluentProvider>
  );
}
