"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { loginUser } from "@/services/authApi";
import {
  getAccessToken,
  setAccessToken,
} from "@/lib/auth";


export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  useEffect(() => {
    const token = getAccessToken();

    if (token) {
      router.replace("/");
    }
  }, [router]);


  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setError("");


    if (!email.trim()) {
      setError("Please enter your email.");
      return;
    }


    if (!password) {
      setError("Please enter your password.");
      return;
    }


    setLoading(true);


    try {
      const result = await loginUser({
        email: email.trim(),
        password,
      });


      setAccessToken(
        result.access_token
      );


      router.replace("/");

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : "Login failed."
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
              Sign in
            </h1>

            <p className="mt-2 text-sm text-slate-500">
              Sign in to continue to your interview preparation workspace.
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
                autoComplete="current-password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="Enter your password"
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
                ? "Signing in..."
                : "Sign in"}
            </button>

          </form>


          <div className="mt-6 border-t border-slate-200 pt-6 text-center">

            <p className="text-sm text-slate-500">
              Don't have an account?
            </p>

            <Link
              href="/register"
              className="mt-1 inline-block text-sm font-medium text-slate-900 hover:underline"
            >
              Create an account
            </Link>

          </div>

        </div>

      </div>

    </main>
  );
}