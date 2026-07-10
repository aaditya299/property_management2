import { useState, useEffect } from 'react'

function PropertyList() {
  const [properties, setProperties] = useState([])

  useEffect(() => {
    fetch('http://localhost:8000/properties')
      .then(res => res.json())
      .then(data => setProperties(data.properties))
  }, [])

  return (
    <div>
      <h2>Available Properties</h2>
      <ul>
        {properties.map(p => (
          <li key={p.property_id}>
            {p.address}, {p.city} — ${p.monthly_rent}/mo — {p.status}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default PropertyList