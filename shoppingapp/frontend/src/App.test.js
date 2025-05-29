import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders signup form by default", () => {
  render(<App />);
  const signupHeading = screen.getByText(/signup/i);
  expect(signupHeading).toBeInTheDocument();
});

test("renders username and password inputs", () => {
  render(<App />);
  const usernameInput = screen.getByPlaceholderText(/username/i);
  const passwordInput = screen.getByPlaceholderText(/password/i);
  expect(usernameInput).toBeInTheDocument();
  expect(passwordInput).toBeInTheDocument();
});
