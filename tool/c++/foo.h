#ifndef FOO_H
# define FOO_H
# include <iostream>
# include <string>
# include <vector>
# include <algorithm>

using namespace std;

typedef struct var_set
{
	int **df_x;
	int year;
	int month;
	int nEMPLOYEE, nDAY;
	int nK, nT, nR, nW, mDAY, nSOL;
	int timelimit;
	int gen;
	int **A_t;
	int **DEMAND;
	int *nightdaylimit;
	vector<int> night;
	vector<int> morning;
	vector<int> noon;
	vector<int> all;
	vector<int> other;
	vector<int> phone;
	vector<vector<int> > D_WEEK;
	int *Dates;
	int *DAY;
	vector<vector<int> > s_break;
	string *Shift_name;
	int *WEEK_of_DAY;
	int P0;
	int P1;
	int P2;
	int P3;
	int P4;
} VAR;

void base_var(VAR *var, char**argv) //傳入基本參數
{
	var->year = atoi(argv[4]);
	var->month = atoi(argv[5]);
	var->nEMPLOYEE = atoi(argv[6]);
	var->nDAY = atoi(argv[7]);
	var->nK = atoi(argv[8]);
	var->nT = atoi(argv[9]);
	var->nR = atoi(argv[10]);
	var->nW = atoi(argv[11]);
	var->mDAY = atoi(argv[12]);
	var->P0 = atoi(argv[14]);
	var->P1 = atoi(argv[15]);
	var->P2 = atoi(argv[16]);
	var->P3 = atoi(argv[17]);
	var->P4 = atoi(argv[18]);
}

void input_A_t(VAR *var, char **argv)
{
	var->A_t = new int*[var->nK];
	string A_t_s = argv[1];
	for (int k = 0; k < var->nK; k++)
	{
		var->A_t[k] = new int[var->nT];
		string input = A_t_s.substr(0,A_t_s.find(",!"));
		A_t_s = A_t_s.substr(A_t_s.find(",!") + 2,A_t_s.length());
		//cout << input << endl;
		
		for (int s = 0; s < var->nT; s++)
		{
			if (s + 1 != var->nT)
			{
				string temp = input.substr(0,input.find(","));
				//cout << temp << endl;
				var->A_t[k][s] = stoi(temp);
				input = input.substr(input.find(",") + 1,input.length());
			}
			else
				var->A_t[k][s] = stoi(input);
		}
	}
	/*
	for (int k = 0; k < var->nK; k++)
	{
		for (int s = 0; s < var->nT; s++)
			cout << var->A_t[k][s]  << " ";
		cout << endl;
	}
	*/
}

void input_D_WEEK(VAR *var, char **argv)
{
	string D_WEEK_s = argv[28];
	while (D_WEEK_s.length() != 0)
	{
		string input =  D_WEEK_s.substr(0,D_WEEK_s.find(",!"));
		D_WEEK_s = D_WEEK_s.substr(D_WEEK_s.find(",!") + 2,D_WEEK_s.length());
		vector<int> temp;
		while (input.find(",") != std::string::npos)
		{
			string num = input.substr(0,input.find(","));
			temp.push_back(stoi(num));
			input = input.substr(input.find(",") + 1,input.length());
		}
		temp.push_back(stoi(input));
		var->D_WEEK.push_back(temp);
	}
}

void input_Dates(VAR *var, char **argv)
{
	string Dates_s = argv[27];
	var->Dates = new int[var->nDAY];
	//cout << Dates_s << endl;
	for (int i = 0; i < var->nDAY; i++)
	{
		string input =  Dates_s.substr(0,Dates_s.find(","));
		Dates_s = Dates_s.substr(Dates_s.find(",") + 1,Dates_s.length());
		var->Dates[i] = stoi(input);
	}
}

void input_DAY(VAR *var, char **argv)
{
	string DAY_s = argv[26];
	var->DAY = new int[var->nDAY];
	for (int i = 0; i < var->nDAY; i++)
	{
		string input =  DAY_s.substr(0,DAY_s.find(","));
		DAY_s = DAY_s.substr(DAY_s.find(",") + 1,DAY_s.length());
		var->DAY[i] = stoi(input);
	}
}

void input_DEMANDS(VAR *var, char **argv)
{
	string DEMANDS_s = argv[13];
	var->DEMAND = new int*[var->nDAY];
	for (int i = 0; i < var->nDAY; i++)
	{
		string input =  DEMANDS_s.substr(0,DEMANDS_s.find(",!"));
		DEMANDS_s = DEMANDS_s.substr(DEMANDS_s.find(",!") + 2,DEMANDS_s.length());
		var->DEMAND[i] = new int[var->nT];
		for (int j = 0; j < var->nT; j++)
		{
			if (j + 1 != var->nT)
			{
				string temp = input.substr(0,input.find(","));
				//cout << temp << endl;
				var->DEMAND[i][j] = stoi(temp);
				input = input.substr(input.find(",") + 1,input.length());
			}
			else
				var->DEMAND[i][j] = stoi(input);
		}
	}
}

void input_nigtdaylimit(VAR *var, char **argv)
{
	string nightdaylimit_s = argv[3];
	var->nightdaylimit = new int[var->nEMPLOYEE];
	for (int i = 0; i < var->nEMPLOYEE; i++)
	{
		string input =  nightdaylimit_s.substr(0,nightdaylimit_s.find(","));
		nightdaylimit_s = nightdaylimit_s.substr(nightdaylimit_s.find(",") + 1,nightdaylimit_s.length());
		var->nightdaylimit[i] = stoi(input);
	}
}

void input_s_break(VAR *var, char **argv)
{
	string s_break_s = argv[25];
	while (s_break_s.length() != 0)
	{
		string input =  s_break_s.substr(0,s_break_s.find(",!"));
		s_break_s = s_break_s.substr(s_break_s.find(",!") + 2,s_break_s.length());
		vector<int> temp;
		while (input.find(",") != std::string::npos)
		{
			string num = input.substr(0,input.find(","));
			temp.push_back(stoi(num));
			input = input.substr(input.find(",") + 1,input.length());
		}
		temp.push_back(stoi(input));
		var->s_break.push_back(temp);
	}
}

void input_SHITset(VAR *var, char **argv)
{
	string all_s = argv[19];
	while (all_s.length() != 0)
	{
		string input =  all_s.substr(0,all_s.find(","));
		all_s = all_s.substr(all_s.find(",") + 1,all_s.length());
		var->all.push_back(stoi(input));
	}

	string morning_s = argv[20];
	while (morning_s.length() != 0)
	{
		string input =  morning_s.substr(0,morning_s.find(","));
		morning_s = morning_s.substr(morning_s.find(",") + 1,morning_s.length());
		var->morning.push_back(stoi(input));
	}
	
	string noon_s = argv[21];
	while (noon_s.length() != 0)
	{
		string input =  noon_s.substr(0,noon_s.find(","));
		noon_s = noon_s.substr(noon_s.find(",") + 1,noon_s.length());
		var->noon.push_back(stoi(input));
	}
	
	string night_s = argv[22];
	while (night_s.length() != 0)
	{
		string input =  night_s.substr(0,night_s.find(","));
		night_s = night_s.substr(night_s.find(",") + 1,night_s.length());
		var->night.push_back(stoi(input));
	}
	
	string phone_s = argv[23];
	while (phone_s.length() != 0)
	{
		string input =  phone_s.substr(0,phone_s.find(","));
		phone_s = phone_s.substr(phone_s.find(",") + 1,phone_s.length());
		var->phone.push_back(stoi(input));
	}
	
	string other_s = argv[24];
	while (other_s.length() != 0)
	{
		string input =  other_s.substr(0,other_s.find(","));
		other_s = other_s.substr(other_s.find(",") + 1,other_s.length());
		var->other.push_back(stoi(input));
	}
}

void input_Shift_name(VAR *var, char **argv)
{
	string Shift_name_s = argv[2];
	var->Shift_name = new string[var->nK];
	for (int i = 0; i < var->nK; i++)
	{
		string input =  Shift_name_s.substr(0,Shift_name_s.find(","));
		Shift_name_s = Shift_name_s.substr(Shift_name_s.find(",") + 1,Shift_name_s.length());
		var->Shift_name[i] = input;
	}
}

void input_WEEK_of_DAY(VAR *var, char **argv)
{
	string WEEK_of_DAY_s = argv[29];
	var->WEEK_of_DAY = new int[var->nDAY];
	for (int i = 0; i < var->nDAY; i++)
	{
		string input =  WEEK_of_DAY_s.substr(0,WEEK_of_DAY_s.find(","));
		WEEK_of_DAY_s = WEEK_of_DAY_s.substr(WEEK_of_DAY_s.find(",") + 1,WEEK_of_DAY_s.length());
		var->WEEK_of_DAY[i] = stoi(input);
	}
}

void input_df_x(VAR *var, char **argv)
{
	string df_x_s = argv[30];
	var->df_x = new int*[var->nEMPLOYEE];
	for (int i = 0; i < var->nEMPLOYEE; i++)
	{
		string input =  df_x_s.substr(0,df_x_s.find(",!"));
		df_x_s = df_x_s.substr(df_x_s.find(",!") + 2,df_x_s.length());
		var->df_x[i] = new int[var->nDAY];
		for (int j = 0; j < var->nDAY; j++)
		{
			if (j + 1 != var->nDAY)
			{
				string temp = input.substr(0,input.find(","));
				//cout << temp << endl;
				var->df_x[i][j] = stoi(temp);
				input = input.substr(input.find(",") + 1,input.length());
			}
			else
				var->df_x[i][j] = stoi(input);
		}
	}

}

void read_fromfile(VAR *var, char **argv)
{
	base_var(var, argv);
	input_A_t(var, argv);
	input_D_WEEK(var, argv);
	input_Dates(var, argv);
	input_DAY(var, argv);
	input_DEMANDS(var, argv);
	input_nigtdaylimit(var, argv);
	input_s_break(var, argv);
	input_SHITset(var, argv);
	input_Shift_name(var, argv);
	input_WEEK_of_DAY(var, argv);
	input_df_x(var, argv);
}

#endif
