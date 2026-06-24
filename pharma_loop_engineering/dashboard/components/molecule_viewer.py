"""Molecular visualization component for the dashboard."""

from typing import Dict, Any, List, Optional, Tuple
import io
import base64
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

from loguru import logger


class MoleculeViewer:
    """Component for rendering and analyzing molecular structures."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.output_dir = Path(self.config.get('output_dir', 'molecule_visualizations'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("MoleculeViewer initialized")

    def smiles_to_mol(self, smiles: str) -> Optional[Any]:
        """Convert SMILES to RDKit molecule object."""
        try:
            from rdkit import Chem
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                logger.warning(f"Invalid SMILES: {smiles}")
                return None
            return mol
        except ImportError:
            logger.error("RDKit not available")
            return None

    def calculate_properties(self, mol: Any) -> Dict[str, Any]:
        """Calculate physicochemical properties."""
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, Lipinski, rdMolDescriptors

            properties = {
                'MW': Descriptors.MolWt(mol),
                'LogP': Descriptors.MolLogP(mol),
                'HBD': Lipinski.NumHDonors(mol),
                'HBA': Lipinski.NumHAcceptors(mol),
                'TPSA': Descriptors.TPSA(mol),
                'RotBonds': Descriptors.NumRotatableBonds(mol),
                'AromaticRings': Lipinski.NumAromaticRings(mol),
                'HeavyAtoms': mol.GetNumHeavyAtoms(),
                'FractionCSP3': rdMolDescriptors.CalcFractionCSP3(mol),
                'FormalCharge': Chem.GetFormalCharge(mol),
                'RingCount': Lipinski.RingCount(mol)
            }

            # Lipinski Rule of 5 violations
            properties['Lipinski_Violations'] = sum([
                properties['MW'] > 500,
                properties['LogP'] > 5,
                properties['HBD'] > 5,
                properties['HBA'] > 10
            ])

            # Veber rules
            properties['Veber_Violations'] = sum([
                properties['RotBonds'] > 10,
                properties['TPSA'] > 140
            ])

            return properties

        except ImportError as e:
            logger.error(f"RDKit not available: {e}")
            return {}

    def generate_2d_structure(self, mol: Any, size: Tuple[int, int] = (400, 400),
                             highlight_atoms: List[int] = None,
                             highlight_bonds: List[int] = None) -> Optional[Image.Image]:
        """Generate 2D molecular structure image."""
        try:
            from rdkit.Chem import Draw

            # Generate 2D coordinates
            from rdkit.Chem import rdDepictor
            rdDepictor.Compute2DCoords(mol)

            # Create drawing options
            opt = Draw.DrawingOptions()
            opt.bgColor = (1, 1, 1, 0)  # Transparent background
            opt.atomColor = (0, 0, 0, 1)
            opt.bondColor = (0, 0, 0, 1)

            # Highlight specific atoms if provided
            if highlight_atoms:
                opt.highlightColors = [(0.8, 0.2, 0.2, 0.5)] * len(highlight_atoms)

            # Generate image
            img = Draw.MolToImage(mol, size=size, options=opt,
                                 highlightAtoms=highlight_atoms,
                                 highlightBonds=highlight_bonds)
            return img

        except ImportError:
            logger.error("RDKit drawing not available")
            return None
        except Exception as e:
            logger.error(f"Failed to generate 2D structure: {e}")
            return None

    def generate_fingerprint_visualization(self, mol: Any, fp_type: str = 'morgan') -> Optional[Image.Image]:
        """Generate molecular fingerprint visualization."""
        try:
            from rdkit import Chem
            from rdkit.Chem import Draw, AllChem

            # Generate fingerprint
            if fp_type == 'morgan':
                fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=256)
            elif fp_type == 'ecfp':
                fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=1024)
            else:
                from rdkit.Chem import RDKFingerprint
                fp = RDKFingerprint(mol)

            # Convert to list for visualization
            fp_bits = list(fp)

            # Create visualization
            fig_size = (12, 4)
            fig = Draw.FingerprintSimilarity(
                [mol], [mol],
                metric=Draw.TanimotoSimilarity
            )

            # Alternative: bit visualization
            bits_on = [i for i, bit in enumerate(fp_bits) if bit]
            if bits_on:
                # Show first 20 active bits
                active_bits = bits_on[:20]
                img = Draw.MolToImage(mol, size=(400, 300),
                                     highlightAtoms=[],  # Could map bits to atoms
                                     highlightBonds=[])
                return img

            return None

        except ImportError:
            logger.error("RDKit fingerprint not available")
            return None
        except Exception as e:
            logger.error(f"Failed to generate fingerprint: {e}")
            return None

    def calculate_tanimoto_similarity(self, mol1: Any, mol2: Any) -> float:
        """Calculate Tanimoto similarity between two molecules."""
        try:
            from rdkit import DataStructs
            from rdkit.Chem import AllChem

            fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, nBits=2048)
            fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, nBits=2048)

            similarity = DataStructs.TanimotoSimilarity(fp1, fp2)
            return float(similarity)

        except ImportError:
            logger.error("RDKit similarity not available")
            return 0.0
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0

    def compare_molecules(self, smiles1: str, smiles2: str,
                         names: Tuple[str, str] = None) -> Dict[str, Any]:
        """
        Compare two molecules side by side.

        Args:
            smiles1: SMILES of first molecule (original)
            smiles2: SMILES of second molecule (candidate)
            names: Tuple of names for labeling

        Returns:
            Comparison report
        """
        if names is None:
            names = ("Original", "Candidato")

        mol1 = self.smiles_to_mol(smiles1)
        mol2 = self.smiles_to_mol(smiles2)

        if mol1 is None or mol2 is None:
            return {'error': 'Invalid SMILES provided'}

        # Generate images
        img1 = self.generate_2d_structure(mol1)
        img2 = self.generate_2d_structure(mol2)

        # Calculate properties
        props1 = self.calculate_properties(mol1)
        props2 = self.calculate_properties(mol2)

        # Calculate similarity
        similarity = self.calculate_tanimoto_similarity(mol1, mol2)

        # Calculate property differences
        prop_diff = {}
        for key in props1:
            if key in props2:
                v1 = props1[key]
                v2 = props2[key]
                if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                    prop_diff[key] = {
                        'original': v1,
                        'candidate': v2,
                        'delta': v2 - v1,
                        'percent_change': ((v2 - v1) / abs(v1) * 100) if v1 != 0 else 0
                    }

        comparison = {
            'names': names,
            'smiles': [smiles1, smiles2],
            'similarity': {
                'tanimoto': similarity,
                'interpretation': self._interpret_similarity(similarity)
            },
            'properties': {
                names[0]: props1,
                names[1]: props2
            },
            'property_differences': prop_diff,
            'images': {
                names[0]: self._image_to_base64(img1) if img1 else None,
                names[1]: self._image_to_base64(img2) if img2 else None
            }
        }

        return comparison

    def _interpret_similarity(self, similarity: float) -> str:
        """Interpret Tanimoto similarity value."""
        if similarity >= 0.9:
            return "Muy similar (estructuralmente idénticos)"
        elif similarity >= 0.7:
            return "Similar (posible analogo)"
        elif similarity >= 0.5:
            return "Moderadamente similar"
        elif similarity >= 0.3:
            return "Poco similar"
        else:
            return "Muy diferente (nuevo scaffold)"

    def _image_to_base64(self, img: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        if img is None:
            return ""
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def generate_comparison_report(self, comparison: Dict[str, Any]) -> str:
        """Generate HTML report for molecule comparison."""
        if 'error' in comparison:
            return f"<p>Error: {comparison['error']}</p>"

        names = comparison['names']
        similarity = comparison['similarity']

        html = f"""
        <div style='background-color: #1E293B; padding: 20px; border-radius: 10px; color: white;'>
            <h2 style='color: #1E3A8A;'>Comparación Molecular</h2>

            <div style='display: flex; gap: 20px; margin: 20px 0;'>
                <div style='flex: 1; text-align: center;'>
                    <h3>{names[0]}</h3>
                    <img src='data:image/png;base64,{comparison["images"][names[0]]}' style='max-width: 100%;'>
                    <p><code>{comparison["smiles"][0][:50]}...</code></p>
                </div>
                <div style='flex: 1; text-align: center;'>
                    <h3>{names[1]}</h3>
                    <img src='data:image/png;base64,{comparison["images"][names[1]]}' style='max-width: 100%;'>
                    <p><code>{comparison["smiles"][1][:50]}...</code></p>
                </div>
            </div>

            <div style='background-color: #0F172A; padding: 15px; border-radius: 8px; margin: 15px 0;'>
                <h4 style='color: #F59E0B;'>Similitud Estructural (Tanimoto)</h4>
                <p style='font-size: 1.5em; color: #10B981;'>{similarity['tanimoto']:.3f}</p>
                <p>{similarity['interpretation']}</p>
            </div>

            <h4 style='color: #1E3A8A;'>Propiedades Fisicoquímicas</h4>
            <table style='width: 100%; border-collapse: collapse;'>
                <tr style='background-color: #334155;'>
                    <th style='padding: 10px;'>Propiedad</th>
                    <th style='padding: 10px;'>{names[0]}</th>
                    <th style='padding: 10px;'>{names[1]}</th>
                    <th style='padding: 10px;'>Delta</th>
                </tr>
        """

        for key, diff in comparison['property_differences'].items():
            color = '#10B981' if abs(diff['percent_change']) < 20 else '#F59E0B'
            html += f"""
                <tr style='border-bottom: 1px solid #334155;'>
                    <td style='padding: 8px;'>{key}</td>
                    <td style='padding: 8px;'>{diff['original']:.2f}</td>
                    <td style='padding: 8px;'>{diff['candidate']:.2f}</td>
                    <td style='padding: 8px; color: {color};'>{diff['delta']:+.2f} ({diff['percent_change']:+.1f}%)</td>
                </tr>
            """

        html += """
            </table>
        </div>
        """

        return html

    def generate_drug_protein_interaction_diagram(self, ligand_smiles: str,
                                                  protein_pdb: str = None,
                                                  binding_site_residues: List[str] = None) -> Optional[Image.Image]:
        """
        Generate drug-protein interaction diagram.

        Args:
            ligand_smiles: SMILES of ligand
            protein_pdb: Path to protein PDB file (optional)
            binding_site_residues: List of binding site residue names

        Returns:
            PIL Image or None
        """
        try:
            from rdkit import Chem
            from rdkit.Chem import Draw

            mol = self.smiles_to_mol(ligand_smiles)
            if mol is None:
                return None

            # Generate 2D structure with highlighted features
            img = self.generate_2d_structure(mol, size=(500, 500))

            # In a full implementation, would:
            # 1. Parse PDB to extract protein structure
            # 2. Perform docking to identify binding pose
            # 3. Render 2D interaction diagram showing:
            #    - Hydrogen bonds
            #    - Hydrophobic interactions
            #    - pi-pi stacking
            #    - Salt bridges

            return img

        except Exception as e:
            logger.error(f"Failed to generate interaction diagram: {e}")
            return None

    def batch_visualize(self, smiles_list: List[str],
                       names: List[str] = None) -> pd.DataFrame:
        """
        Batch visualization of multiple molecules.

        Returns:
            DataFrame with properties and image paths
        """
        if names is None:
            names = [f"Mol_{i}" for i in range(len(smiles_list))]

        results = []

        for smiles, name in zip(smiles_list, names):
            mol = self.smiles_to_mol(smiles)
            if mol is None:
                continue

            properties = self.calculate_properties(mol)
            img = self.generate_2d_structure(mol)

            if img:
                img_path = self.output_dir / f"{name.replace(' ', '_')}.png"
                img.save(img_path)
                properties['image_path'] = str(img_path)

            properties['name'] = name
            properties['smiles'] = smiles
            results.append(properties)

        return pd.DataFrame(results)

    def generate_summary_table(self, molecules: List[Dict[str, Any]]) -> str:
        """Generate HTML summary table of molecule properties."""
        if not molecules:
            return "<p>No molecules to display</p>"

        html = """
        <table style='width: 100%; border-collapse: collapse; background-color: #1E293B; color: white;'>
            <tr style='background-color: #1E3A8A;'>
                <th style='padding: 10px;'>Nombre</th>
                <th style='padding: 10px;'>MW</th>
                <th style='padding: 10px;'>LogP</th>
                <th style='padding: 10px;'>HBD/HBA</th>
                <th style='padding: 10px;'>TPSA</th>
                <th style='padding: 10px;'>Lipinski</th>
            </tr>
        """

        for mol in molecules:
            props = mol.get('properties', {})
            lipinski = f"{props.get('Lipinski_Violations', 0)}/4"
            lipinski_color = '#10B981' if props.get('Lipinski_Violations', 0) <= 1 else '#F59E0B'

            html += f"""
                <tr style='border-bottom: 1px solid #334155;'>
                    <td style='padding: 8px;'>{mol.get('name', 'Unknown')}</td>
                    <td style='padding: 8px;'>{props.get('MW', 0):.1f}</td>
                    <td style='padding: 8px;'>{props.get('LogP', 0):.2f}</td>
                    <td style='padding: 8px;'>{props.get('HBD', 0)}/{props.get('HBA', 0)}</td>
                    <td style='padding: 8px;'>{props.get('TPSA', 0):.1f}</td>
                    <td style='padding: 8px; color: {lipinski_color};'>{lipinski}</td>
                </tr>
            """

        html += "</table>"
        return html

    def calculate_fingerprint_features(self, mol: Any, fp_type: str = 'morgan') -> Dict[str, Any]:
        """Calculate and return fingerprint features for ML."""
        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem, RDKFingerprint
            import pandas as pd

            if fp_type == 'morgan':
                fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
            elif fp_type == 'morgan_counts':
                fp = AllChem.GetCountFingerprint(mol, 2)
            else:
                fp = RDKFingerprint(mol)

            # Convert to numpy array
            fp_array = np.zeros((1,), dtype=np.int32)
            from rdkit.DataStructs import ConvertToNumpyArray
            ConvertToNumpyArray(fp, fp_array)

            return {
                'fingerprint': fp_array.tolist(),
                'n_features': len(fp_array),
                'n_active': int(np.sum(fp_array > 0)),
                'type': fp_type
            }

        except ImportError:
            logger.error("RDKit fingerprints not available")
            return {}
        except Exception as e:
            logger.error(f"Failed to calculate fingerprint: {e}")
            return {}

    def __repr__(self) -> str:
        return f"MoleculeViewer(output_dir={self.output_dir})"


if __name__ == "__main__":
    # Test the viewer
    viewer = MoleculeViewer()

    test_smiles = [
        "CN(C)C(=O)N(C)C",  # Metformin
        "CC(=O)Oc1ccccc1C(=O)O",  # Aspirin
    ]

    for smiles in test_smiles:
        mol = viewer.smiles_to_mol(smiles)
        if mol:
            props = viewer.calculate_properties(mol)
            print(f"Properties: {props}")

            img = viewer.generate_2d_structure(mol)
            if img:
                img_path = viewer.output_dir / "test_structure.png"
                img.save(img_path)
                print(f"Saved structure to {img_path}")