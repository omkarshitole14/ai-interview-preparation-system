"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { registerUser } from "@/services/authApi";


export default function RegisterPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setError("");


    if (!email.trim()) {
      setError("Please enter your email.");
      return;
    }


    if (password.length < 8) {
      setError(
        "Password must contain at least 8 characters."
      );
      return;
    }


    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }


    setLoading(true);


    try {

      await registerUser({
        email: email.trim(),
        password,
      });


      router.replace("/login");

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : "Registration failed."
      );

    } finally {
      setLoading(false);
    }
  };


  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-6">

      <div className="w-full max-w-md">

        <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">

          <div className="mb-8">

            <p className="text-sm font-medium text-blue-600">
              AI Interview System
            </p>

            <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">
              Create your account
            </h1>

            <p className="mt-2 text-sm text-slate-500">
              Create an account to save your resumes and interview sessions.
            </p>

          </div>


          <form
            onSubmit={handleSubmit}
            className="space-y-5"
          >

            <div>

              <label
                htmlFor="email"
                className="text-sm font-medium text-slate-700"
              >
                Email
              </label>

              <input
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                placeholder="you@example.com"
                className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-100"
                />

            </div>


            <div>

              <label
                htmlFor="password"
                className="text-sm font-medium text-slate-700"
              >
                Password
              </label>

              <input
                id="password"
                type="password"
                autoComplete="new-password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="At least 8 characters"
                className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-100"
            />
                </div>


            <div>

              <label
                htmlFor="confirmPassword"
                className="text-sm font-medium text-slate-700"
              >
                Confirm password
              </label>

              <input
                id="confirmPassword"
                type="password"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(event) =>
                  setConfirmPassword(
                    event.target.value
                  )
                }
                placeholder="Enter password again"
                className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-100"
              />

            </div>


            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}


            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading
                ? "Creating account..."
                : "Create account"}
            </button>

          </form>


          <div className="mt-6 border-t border-slate-200 pt-6 text-center">

            <p className="text-sm text-slate-500">
              Already have an account?
            </p>

            <Link
              href="/login"
              className="mt-1 inline-block text-sm font-medium text-slate-900 hover:underline"
            >
              Sign in
            </Link>

          </div>

        </div>

      </div>

    </main>
  );
}