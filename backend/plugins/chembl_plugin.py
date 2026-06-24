"""ChEMBL plugin for accessing chemical database."""

from typing import Dict, Any, List, Optional
import time
import json
from pathlib import Path
from loguru import logger


class ChEMBLPlugin:
    """Plugin for ChEMBL database interactions with full API coverage."""

    BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"
    CACHE_TTL = 3600  # 1 hour

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache: Dict[str, Any] = {}
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 1)
        self.user_agent = config.get('user_agent', 'PharmaLoop/1.0')
        logger.info("ChEMBLPlugin initialized")

    def _retry_request(self, method, url, **kwargs):
        """Retry HTTP requests with backoff."""
        import requests
        attempt = 0
        last_error = None
        while attempt < self.max_retries:
            try:
                response = requests.request(method, url, timeout=30, **kwargs)
                response.raise_for_status()
                return response
            except Exception as e:
                last_error = e
                logger.warning(f"ChEMBL request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                attempt += 1
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        raise last_error

    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached response if not expired."""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.CACHE_TTL:
                return entry['data']
            else:
                del self.cache[key]
        return None

    def _set_cache(self, key: str, data: Any) -> None:
        """Store response in cache."""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }

    def get_compound(self, chembl_id: str) -> Dict[str, Any]:
        """
        Get compound data by ChEMBL ID.

        Args:
            chembl_id: ChEMBL molecule ID (e.g., CHEMBL1234)

        Returns:
            Compound data dictionary
        """
        cache_key = f"compound_{chembl_id}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            import requests
            url = f"{self.BASE_URL}/molecule/{chembl_id}.json"
            response = self._retry_request('GET', url)
            data = response.json()

            compound = {
                'chembl_id': data.get('molecule_chembl_id'),
                'name': data.get('pref_name'),
                'formula': data.get('molecule_properties', {}).get('full_mol_formula'),
                'mw': data.get('molecule_properties', {}).get('full_mwt'),
                ' smiles': data.get('molecule_structures', {}).get('canonical_smiles'),
                'inchi': data.get('molecule_structures', {}).get('inchi'),
                'inchikey': data.get('molecule_structures', {}).get('inchikey'),
                'alogp': data.get('molecule_properties', {}).get('alogp'),
                'psa': data.get('molecule_properties', {}).get('psa'),
                'hbd': data.get('molecule_properties', {}).get('hbd'),
                'hba': data.get('molecule_properties', {}).get('hba'),
                'heavy_atoms': data.get('molecule_properties', {}).get('heavy_atoms'),
                'source': 'chembl'
            }

            self._set_cache(cache_key, compound)
            return compound

        except Exception as e:
            logger.error(f"Failed to get compound {chembl_id}: {e}")
            return {}

    def search_target(self, protein_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search therapeutic targets by protein name.

        Args:
            protein_name: Protein name (e.g., 'EGFR', 'BRCA1')
            limit: Maximum results

        Returns:
            List of target dictionaries
        """
        cache_key = f"target_{protein_name}_{limit}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            import requests
            url = f"{self.BASE_URL}/target/search.json"
            params = {'q': protein_name, 'limit': limit}
            response = self._retry_request('GET', url, params=params)
            data = response.json()

            targets = []
            for t in data.get('targets', []):
                targets.append({
                    'target_chembl_id': t.get('target_chembl_id'),
                    'name': t.get('target_name'),
                    'target_type': t.get('target_type'),
                    'organism': t.get('target_chembl_id'),  # Often contains organism info
                    'source': 'chembl'
                })

            self._set_cache(cache_key, targets)
            return targets

        except Exception as e:
            logger.error(f"Failed to search target {protein_name}: {e}")
            return []

    def get_activity_data(self, compound_id: str, target_id: str,
                         activity_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get bioactivity data for a compound-target pair.

        Args:
            compound_id: ChEMBL molecule ID
            target_id: ChEMBL target ID
            activity_types: List of activity types (IC50, EC50, Ki, etc.)

        Returns:
            List of activity records with normalized data
        """
        if activity_types is None:
            activity_types = ['IC50', 'EC50', 'Ki', 'Kd', 'GI50']

        cache_key = f"activity_{compound_id}_{target_id}_{'_'.join(activity_types)}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            import requests
            import pandas as pd
            import numpy as np

            url = f"{self.BASE_URL}/activity.json"
            all_activities = []

            for act_type in activity_types:
                params = {
                    'molecule_chembl_id': compound_id,
                    'target_chembl_id': target_id,
                    'standard_type': act_type,
                    'limit': 100,
                    'order_by': 'standard_value',
                    'order_dir': 'asc'
                }

                response = self._retry_request('GET', url, params=params)
                data = response.json()
                activities = data.get('activities', [])
                all_activities.extend(activities)

            # Process and normalize
            results = []
            for act in all_activities:
                value = act.get('standard_value')
                units = act.get('standard_units', 'nM')

                # Convert to pIC50 if IC50/EC50
                pic50 = None
                if act.get('standard_type') in ['IC50', 'EC50'] and value and value > 0:
                    # Convert nM to M then to pIC50
                    if units == 'nM':
                        value_molar = value * 1e-9
                    elif units == 'uM':
                        value_molar = value * 1e-6
                    elif units == 'mM':
                        value_molar = value * 1e-3
                    else:
                        value_molar = value
                    pic50 = -np.log10(value_molar)

                results.append({
                    'molecule_chembl_id': act.get('molecule_chembl_id'),
                    'target_chembl_id': act.get('target_chembl_id'),
                    'activity_type': act.get('standard_type'),
                    'value': value,
                    'units': units,
                    'pic50': round(pic50, 3) if pic50 else None,
                    'relation': act.get('standard_relation'),
                    'confidence': act.get('data_warning'),
                    'assay_id': act.get('assay_chembl_id'),
                    'pubmed_id': act.get('pubmed_id'),
                    'year': act.get('year'),
                    'source': 'chembl'
                })

            # Filter low quality
            results = [r for r in results if r.get('value') is not None]
            results = [r for r in results if r.get('confidence') not in ['Low confidence', 'Invalid']]

            self._set_cache(cache_key, results)
            return results

        except Exception as e:
            logger.error(f"Failed to get activity data {compound_id}/{target_id}: {e}")
            return []

    def download_dataset(self, target: str, file_format: str = 'csv',
                        output_dir: str = None) -> Optional[str]:
        """
        Download dataset for a target.

        Args:
            target: Target name or ChEMBL ID
            file_format: Output format (csv, json, sdf)
            output_dir: Directory to save file

        Returns:
            Path to downloaded file
        """
        try:
            import requests
            from pathlib import Path

            if output_dir is None:
                output_dir = Path(self.config.get('output_dir', 'data/chembl'))
            else:
                output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Resolve target to ChEMBL ID
            if target.startswith('CHEMBL'):
                target_id = target
            else:
                targets = self.search_target(target, limit=1)
                if not targets:
                    logger.error(f"Target not found: {target}")
                    return None
                target_id = targets[0]['target_chembl_id']

            url = f"{self.BASE_URL}/activity.json"
            params = {
                'target_chembl_id': target_id,
                'limit': 1000,
                'order_by': 'standard_value',
                'order_dir': 'asc'
            }

            response = self._retry_request('GET', url, params=params)
            data = response.json()
            activities = data.get('activities', [])

            if not activities:
                logger.warning(f"No activities found for target: {target}")
                return None

            # Convert to DataFrame
            import pandas as pd
            df = pd.DataFrame(activities)

            # Save file
            filename = f"{target_id}_activities.{file_format}"
            output_path = output_dir / filename

            if file_format == 'csv':
                df.to_csv(output_path, index=False)
            elif file_format == 'json':
                df.to_json(output_path, orient='records', indent=2)
            elif file_format == 'sdf':
                # Would need RDKit for SDF conversion
                df.to_csv(output_path, index=False)
                logger.warning("SDF format requires RDKit, saved as CSV instead")

            logger.success(f"Dataset downloaded: {output_path} ({len(df)} records)")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to download dataset for {target}: {e}")
            return None

    def batch_get_compounds(self, chembl_ids: List[str]) -> pd.DataFrame:
        """
        Get multiple compounds by ChEMBL IDs.

        Args:
            chembl_ids: List of ChEMBL IDs

        Returns:
            DataFrame with compound data
        """
        import pandas as pd

        compounds = []
        for cid in chembl_ids:
            data = self.get_compound(cid)
            if data:
                compounds.append(data)

        return pd.DataFrame(compounds)

    def search_compounds_by_smiles(self, smiles: str, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Search similar compounds by SMILES.

        Args:
            smiles: Query SMILES string
            similarity_threshold: Minimum similarity (0-1)

        Returns:
            List of similar compounds
        """
        cache_key = f"similar_{smiles}_{similarity_threshold}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            import requests

            url = f"{self.BASE_URL}/similarity.json"
            params = {
                'smiles': smiles,
                'threshold': similarity_threshold,
                'limit': 50
            }

            response = self._retry_request('GET', url, params=params)
            data = response.json()

            compounds = []
            for match in data.get('molecules', []):
                compounds.append({
                    'chembl_id': match.get('chembl_id'),
                    'name': match.get('pref_name'),
                    'smiles': match.get('canonical_smiles'),
                    'similarity': match.get('similarity'),
                    'source': 'chembl'
                })

            self._set_cache(cache_key, compounds)
            return compounds

        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []

    def get_indications(self, chembl_id: str) -> List[Dict[str, Any]]:
        """
        Get drug indications for a compound.

        Args:
            chembl_id: ChEMBL molecule ID

        Returns:
            List of indications
        """
        cache_key = f"indications_{chembl_id}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            import requests
            url = f"{self.BASE_URL}/drug_indication.json"
            params = {'molecule_chembl_id': chembl_id}
            response = self._retry_request('GET', url, params=params)
            data = response.json()

            indications = []
            for ind in data.get('drug_indications', []):
                indications.append({
                    'mesh_id': ind.get('mesh_id'),
                    'mesh_heading': ind.get('mesh_heading'),
                    'efo_id': ind.get('efo_id'),
                    'efo_term': ind.get('efo_term'),
                    'source': 'chembl'
                })

            self._set_cache(cache_key, indications)
            return indications

        except Exception as e:
            logger.error(f"Failed to get indications for {chembl_id}: {e}")
            return []


# Usage examples
if __name__ == "__main__":
    plugin = ChEMBLPlugin({})

    # Example 1: EGFR target
    print("=== EGFR Example ===")
    egfr_targets = plugin.search_target("EGFR")
    if egfr_targets:
        print(f"Found EGFR target: {egfr_targets[0]['target_chembl_id']}")

    # Example 2: BRCA1 target
    print("\n=== BRCA1 Example ===")
    brca1_targets = plugin.search_target("BRCA1")
    if brca1_targets:
        print(f"Found BRCA1 target: {brca1_targets[0]['target_chembl_id']}")

    # Example 3: ACE2 target
    print("\n=== ACE2 Example ===")
    ace2_targets = plugin.search_target("ACE2")
    if ace2_targets:
        print(f"Found ACE2 target: {ace2_targets[0]['target_chembl_id']}")

    # Example 4: Get compound data
    print("\n=== Compound Example ===")
    compound = plugin.get_compound("CHEMBL113")  # Aspirin
    if compound:
        print(f"Compound: {compound['name']}, MW: {compound['mw']}")

    print("\n=== Cache Stats ===")
    print(f"Cached entries: {len(plugin.cache)}")