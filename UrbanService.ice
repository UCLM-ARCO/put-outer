// State: PROPOSAL
module UrbanService{
  struct position3D{
    float x;
    float y;
    float z;
  };

  sequence<position3D> LinearRing;
  sequence<position3D> LineString;
  sequence<string> IDsequence;

  struct Surface{
    string id;
    LinearRing linearRing;
  };

  sequence<Surface> SurfaceSequence;

  struct Geometry3D{
    string id;
    SurfaceSequence surfaces;
  };

  struct cellSpace{
    string id;
    string name;
    string usage;
    string duality;
    Geometry3D geometry;
    IDsequence cellSpaceBoundaries;
  };

  struct cellSpaceBoundary{
    string id;
    string name;
    string usage;
    string material;
    Geometry3D geometry;
  };

  struct state{
    string id;
    position3D position;
    string name;
    string duality;
  };

  struct transition{
    string id;
    string name;
    float weight;
    string duality;
    string connectsFrom;
    string connectsTo;
    LineString lineString;
  };

  sequence<cellSpace> CellSequence;
  sequence<cellSpaceBoundary> CellSpaceBoundarySequence;
  sequence<state> StateSequence;
  sequence<transition> TransitionSequence;

  interface IgmlLayer{
    bool isConnectedCell(string referenceCellID, string cellToCheqID);
    bool isAdjacentCell(string referenceCellID, string cellToCheqID);
    //bool isAccesibleCell(string referenceCellID, string cellToCheqID);

    IDsequence getConnectedCells(string referenceCellID);
    IDsequence getAdjacentCells(string referenceCellID);
    //IDsequence getAccesibleCells(string referenceCellID);

    IDsequence getCellSpaceBoundariesBetweenCells(string referenceCellID1, string referenceCellID2);

    CellSequence getCells(string spaceLayerID);
    CellSpaceBoundarySequence getCellSpaceBoundaries(string spaceLayerID);
    StateSequence getStates(string spaceLayerID);
    TransitionSequence getTransitions(string spaceLayerID);

    string getCellofPosition(string spaceLayerID, position3D position);
    bool isPositionInCell(position3D position, string cell);
    IDsequence getPathCellToCell(string spaceLayerID, string CellIDfrom, string CellIDto);
    IDsequence getPathPositionToPosition(string spaceLayerID, position3D positionFrom, position3D positionTo);

    string getUsage(string referenceCellID);
    string getName(string referenceCellID);
    float getHeight(string referenceCellID);

    IDsequence getExits(string referenceCellID);
    IDsequence getEntrances(string spaceLayerID);

    IDsequence getSpaceLayersID();
  };
};
