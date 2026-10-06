import React, { useState } from 'react';
import { COMPLAINT_CATEGORIES } from '../../utils/constants';
import ImageUpload from './ImageUpload';
import LocationPicker from './LocationPicker';
import { validateComplaint } from '../../utils/validators';

const ComplaintForm = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    category: '',
    description: '',
    address: '',
    image: null,
    location: null,
  });
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const handleImageSelect = (file) => {
    setFormData((prev) => ({ ...prev, image: file }));
    if (errors.image) {
      setErrors((prev) => ({ ...prev, image: null }));
    }
  };

  const handleLocationSelect = (location) => {
    setFormData((prev) => ({ ...prev, location }));
    if (errors.location) {
      setErrors((prev) => ({ ...prev, location: null }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    let { valid, errors: validationErrors } = validateComplaint(formData);

    if (!formData.image) {
      validationErrors.image = 'An image of the infrastructure issue is required';
      valid = false;
    }

    if (!formData.location) {
      validationErrors.location = 'Please select a location on the map or use your GPS';
      valid = false;
    }

    if (!valid) {
      setErrors(validationErrors);
      return;
    }

    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-[#111827]/90 p-6 sm:p-8 rounded-2xl shadow-xl border border-slate-800">
      <div>
        <label className="block text-sm font-semibold text-slate-200 mb-1.5">
          Complaint Category <span className="text-rose-400">*</span>
        </label>
        <select
          name="category"
          value={formData.category}
          onChange={handleChange}
          className={`w-full p-3 bg-slate-900 border rounded-xl text-slate-200 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all ${
            errors.category ? 'border-rose-500' : 'border-slate-700'
          }`}
        >
          <option value="" className="bg-slate-900 text-slate-400">Select issue category</option>
          {COMPLAINT_CATEGORIES.map((cat) => (
            <option key={cat.value} value={cat.value} className="bg-slate-900 text-slate-200">
              {cat.label}
            </option>
          ))}
        </select>
        {errors.category && <p className="mt-1.5 text-xs text-rose-400">{errors.category}</p>}
      </div>

      <div>
        <label className="block text-sm font-semibold text-slate-200 mb-1.5">
          Description <span className="text-rose-400">*</span>
        </label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows="4"
          placeholder="Describe the issue, hazards, or notable landmarks (minimum 5 characters)..."
          className={`w-full p-3 bg-slate-900 border rounded-xl text-slate-200 placeholder-slate-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all ${
            errors.description ? 'border-rose-500' : 'border-slate-700'
          }`}
        />
        {errors.description && <p className="mt-1.5 text-xs text-rose-400">{errors.description}</p>}
      </div>

      <div>
        <label className="block text-sm font-semibold text-slate-200 mb-1.5">
          Street Address / Landmark <span className="text-xs font-normal text-slate-400">(Optional)</span>
        </label>
        <input
          type="text"
          name="address"
          value={formData.address}
          onChange={handleChange}
          placeholder="e.g., Near Main Market Junction, Sector 4"
          className="w-full p-3 bg-slate-900 border border-slate-700 rounded-xl text-slate-200 placeholder-slate-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all"
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-slate-200 mb-1.5">
          Upload Evidence Photo <span className="text-rose-400">*</span>
        </label>
        <ImageUpload onImageSelect={handleImageSelect} currentImage={formData.image} />
        {errors.image && <p className="mt-1.5 text-xs text-rose-400">{errors.image}</p>}
      </div>

      <div>
        <label className="block text-sm font-semibold text-slate-200 mb-1.5">
          Pin Location on Map <span className="text-rose-400">*</span>
        </label>
        <LocationPicker onLocationSelect={handleLocationSelect} />
        {errors.location && <p className="mt-1.5 text-xs text-rose-400">{errors.location}</p>}
      </div>

      <div className="pt-4 border-t border-slate-800">
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-purple-600 hover:bg-purple-500 text-white font-semibold py-3.5 px-4 rounded-xl transition-all shadow-lg shadow-purple-600/30 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2"
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Uploading & Dispatching AI Pipeline...</span>
            </>
          ) : (
            'Submit Complaint'
          )}
        </button>
      </div>
    </form>
  );
};

export default ComplaintForm;
