import { useState } from "react";
import { createLead } from "../services/api";

const EMPTY_FORM = {
  full_name: "",
  email: "",
  phone: "",
  company: "",
  requirement: "",
};

/**
 * LeadForm
 * --------
 * The Lead Capture Form. Validates required fields client-side for fast
 * feedback, then submits to POST /lead. The backend re-validates everything
 * regardless (never trust the client), so this is purely for UX.
 */
export default function LeadForm() {
  const [form, setForm] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [successInfo, setSuccessInfo] = useState(null);
  const [submitError, setSubmitError] = useState("");

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    // Clear the field-level error as soon as the user starts fixing it.
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  }

  function validate() {
    const next = {};
    if (!form.full_name.trim()) next.full_name = "Full name is required";
    if (!form.email.trim()) {
      next.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
      next.email = "Enter a valid email address";
    }
    if (!form.phone.trim()) {
      next.phone = "Phone number is required";
    } else if (form.phone.replace(/\D/g, "").length < 7) {
      next.phone = "Enter a valid phone number";
    }
    if (!form.requirement.trim()) next.requirement = "Please describe your requirement";
    return next;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitError("");
    setSuccessInfo(null);

    const validationErrors = validate();
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) return;

    setSubmitting(true);
    try {
      const lead = await createLead({
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim(),
        company: form.company.trim() || null,
        requirement: form.requirement.trim(),
      });
      setSuccessInfo(lead);
      setForm(EMPTY_FORM);
    } catch (err) {
      setSubmitError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-xl mx-auto bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
      <h2 className="text-2xl font-semibold text-gray-900 mb-1">Get In Touch</h2>
      <p className="text-gray-500 mb-6">
        Tell us about your requirement and we'll get back to you shortly.
      </p>

      {successInfo && (
        <div className="mb-6 rounded-lg bg-green-50 border border-green-200 text-green-800 px-4 py-3 text-sm">
          <p className="font-medium">Thanks, {successInfo.full_name.split(" ")[0]}! Your requirement was submitted.</p>
          <p className="mt-1">
            We've sent a confirmation email to <span className="font-medium">{successInfo.email}</span>.
          </p>
          <p className="mt-1 text-green-700">
            Detected category: <span className="font-semibold">{successInfo.category}</span> &middot; Priority:{" "}
            <span className="font-semibold">{successInfo.priority}</span>
          </p>
        </div>
      )}

      {submitError && (
        <div className="mb-6 rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
          {submitError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5" noValidate>
        <Field
          label="Full Name"
          name="full_name"
          required
          value={form.full_name}
          onChange={handleChange}
          error={errors.full_name}
          placeholder="John Smith"
        />

        <Field
          label="Email Address"
          name="email"
          type="email"
          required
          value={form.email}
          onChange={handleChange}
          error={errors.email}
          placeholder="john@example.com"
        />

        <Field
          label="Phone Number"
          name="phone"
          type="tel"
          required
          value={form.phone}
          onChange={handleChange}
          error={errors.phone}
          placeholder="+91 98765 43210"
        />

        <Field
          label="Company Name"
          name="company"
          value={form.company}
          onChange={handleChange}
          placeholder="Acme Inc. (optional)"
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Requirement / Message <span className="text-red-500">*</span>
          </label>
          <textarea
            name="requirement"
            rows={4}
            value={form.requirement}
            onChange={handleChange}
            placeholder="Tell us what you need help with..."
            className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 ${
              errors.requirement ? "border-red-400" : "border-gray-300"
            }`}
          />
          {errors.requirement && <p className="mt-1 text-xs text-red-600">{errors.requirement}</p>}
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-primary-600 hover:bg-primary-700 disabled:opacity-60 disabled:cursor-not-allowed text-white font-medium py-2.5 rounded-lg transition-colors"
        >
          {submitting ? "Submitting..." : "Submit Requirement"}
        </button>
      </form>
    </div>
  );
}

/** Small reusable text input with label + inline error message. */
function Field({ label, name, value, onChange, error, required, type = "text", placeholder }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 ${
          error ? "border-red-400" : "border-gray-300"
        }`}
      />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}
